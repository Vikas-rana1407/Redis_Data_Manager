# app/videos/processor.py

import os
import json
import time
import re
from dotenv import load_dotenv
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)

from app.videos.new_tags import activity_tags, goal_objective_tags
from app.videos.prompt import prepare_prompt
from app.videos.utils import get_video_title, extract_json_response, call_llm, ensure_dirs

load_dotenv()
BASE_DIR = "app/data"
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_transcripts")
ensure_dirs([TRANSCRIPTS_DIR, PROCESSED_DIR])

def extract_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_transcript(video_id: str, lang="en"):
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=[lang])
        text = " ".join(item.text for item in transcript)
        path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Saved transcript to {path}")
        return text
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        print(f"❌ Transcript error for {video_id}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def process_transcript(video_id: str, transcript: str):
    if not transcript:
        print("⚠️ Empty transcript. Skipping.")
        return None

    title = get_video_title(video_id)
    prompt = prepare_prompt(transcript, title, video_id, activity_tags, goal_objective_tags)
    print("📤 Sending to LLM...")
    time.sleep(1)
    llm_response = call_llm(prompt)
    result = extract_json_response(llm_response)

    if not result:
        print("❌ Failed to extract JSON from LLM response.")
        return None

    result["videoId"] = video_id
    result["videoTitle"] = title
    result["transcript_text"] = transcript

    output_path = os.path.join(PROCESSED_DIR, f"{video_id}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(f"✅ Saved processed JSON: {output_path}")
    return result
