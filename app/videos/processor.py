
# app/videos/processor.py
# Handles transcript fetching, LLM processing, and JSON output for YouTube videos.

# Standard library imports
import os
import json
import time
import re

# Third-party imports
from dotenv import load_dotenv
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)

# App imports
from app.videos.new_tags import activity_tags, goal_objective_tags
from app.videos.prompt import prepare_prompt
from app.videos.utils import get_video_title, extract_json_response, call_llm, ensure_dirs
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
BASE_DIR = "app/data"
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_transcripts")
ensure_dirs([TRANSCRIPTS_DIR, PROCESSED_DIR])

def extract_video_id(url: str):
    """
    Extract YouTube video ID from URL.
    Args:
        url (str): YouTube video URL
    Returns:
        str or None: Video ID if found, else None
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_transcript(video_id: str, lang="en"):
    """
    Fetch YouTube transcript and save to file.
    Args:
        video_id (str): YouTube video ID
        lang (str): Language code
    Returns:
        str or None: Transcript text if successful, else None
    """
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=[lang])
        text = " ".join(item.text for item in transcript)
        path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Saved transcript to {path}")
        return text
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        logger.error(f"Transcript error for {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching transcript for {video_id}: {e}")
        return None

def process_transcript(video_id: str, transcript: str):
    """
    Process transcript with LLM and save structured JSON output.
    Args:
        video_id (str): YouTube video ID
        transcript (str): Transcript text
    Returns:
        dict or None: Processed result if successful, else None
    """
    if not transcript:
        logger.warning("Empty transcript. Skipping.")
        return None

    title = get_video_title(video_id)
    prompt = prepare_prompt(transcript, title, video_id, activity_tags, goal_objective_tags)
    logger.info(f"Sending transcript for video {video_id} to LLM...")
    time.sleep(1)
    llm_response = call_llm(prompt)
    if not llm_response:
        logger.error("LLM did not return a response.")
        return None
    result = extract_json_response(llm_response)

    if not result:
        logger.error("Failed to extract JSON from LLM response.")
        return None

    result["videoId"] = video_id
    result["videoTitle"] = title
    result["transcript_text"] = transcript

    output_path = os.path.join(PROCESSED_DIR, f"{video_id}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    logger.info(f"Saved processed JSON: {output_path}")
    return result
