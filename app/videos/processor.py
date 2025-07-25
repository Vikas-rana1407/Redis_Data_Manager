import os
import json
import time
import requests
from app.redis_manager import RedisManager
from app.videos.prompt import prepare_prompt
from app.videos.new_tags import activity_tags
from dotenv import load_dotenv
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from bs4 import BeautifulSoup
from openai import OpenAI
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()
DEEPINFRA_TOKEN = os.getenv('DEEPINFRA_TOKEN')
TRANSCRIPTS_FOLDER = os.path.join(os.path.dirname(__file__), '../data/transcripts')
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), '../data/processed_transcripts')
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

class YouTubeProcessor:
    """
    Handles addition and processing of YouTube videos:
    - Fetch transcript
    - Tag with LLM
    - Save processed data to Redis
    """
    def __init__(self):
        self.redis = RedisManager()

    def extract_video_id(self, url: str):
        """Extract YouTube video ID from URL."""
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
        return match.group(1) if match else None

    def fetch_transcript(self, video_id: str, lang='en'):
        """Fetch transcript for a YouTube video."""
        try:
            fetched = YouTubeTranscriptApi().fetch(video_id, languages=[lang])
            paragraph = ' '.join(entry.text for entry in fetched)
            path = os.path.join(TRANSCRIPTS_FOLDER, f'{video_id}.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(paragraph)
            logger.info(f'Saved transcript: {path}')
            return paragraph
        except NoTranscriptFound:
            logger.error(f'No transcript found for video {video_id}')
        except TranscriptsDisabled:
            logger.error('Transcripts are disabled.')
        except VideoUnavailable:
            logger.error('Video is unavailable.')
        except Exception as e:
            logger.error(f'Error: {e}')
        return None

    def get_video_title(self, video_id: str):
        """Fetch video title from YouTube."""
        try:
            url = f'https://www.youtube.com/watch?v={video_id}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            tag = soup.find('title')
            return tag.get_text().replace('- YouTube', '').strip() if tag else 'Unknown Title'
        except Exception as e:
            logger.error(f'Title fetch failed: {e}')
            return 'Unknown Title'

    def call_llm(self, prompt: str):
        """Call LLM to tag video transcript."""
        openai = OpenAI(
            api_key=DEEPINFRA_TOKEN,
            base_url='https://api.deepinfra.com/v1/openai',
        )
        completion = openai.chat.completions.create(
            model='deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
            messages=[{'role': 'user', 'content': prompt}],
            stream=False,
        )
        return completion.choices[0].message.content

    def extract_json_response(self, response: str):
        """Extract JSON from LLM response."""
        match = re.search(r'```json(.*?)```', response, re.DOTALL)
        json_text = match.group(1).strip() if match else response.strip()
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f'JSON parse failed: {e}')
            return None

    def process_transcript(self, video_id: str, transcript_text: str):
        """Process transcript, tag, and save to Redis."""
        if not transcript_text:
            logger.warning('Empty transcript. Skipping.')
            return
        title = self.get_video_title(video_id)
        prompt = prepare_prompt(transcript_text, title, video_id, activity_tags)
        logger.info('Sending to LLM...')
        time.sleep(1)
        response = self.call_llm(prompt)
        result_json = self.extract_json_response(response)
        if not result_json:
            logger.error('Failed to extract JSON.')
            return
        result_json['videoId'] = video_id
        result_json['videoTitle'] = title
        result_json['transcript_text'] = transcript_text
        out_path = os.path.join(PROCESSED_FOLDER, f'{video_id}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result_json, f, indent=4)
        logger.info(f'Saved processed JSON: {out_path}')
        self.redis.set_json(f'video:{video_id}', result_json)
        logger.info(f'Stored in Redis: video:{video_id}')

    def process_video_url(self, youtube_url: str):
        """Process a YouTube video URL: fetch transcript, tag, and save."""
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            logger.error('Invalid YouTube URL')
            return
        logger.info(f'Processing Video ID: {video_id}')
        transcript_path = os.path.join(TRANSCRIPTS_FOLDER, f'{video_id}.txt')
        if os.path.exists(transcript_path):
            logger.info(f'Transcript already exists for {video_id}')
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
        else:
            transcript = self.fetch_transcript(video_id)
        if transcript:
            self.process_transcript(video_id, transcript)
