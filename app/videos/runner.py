
# app/videos/runner.py
# Orchestrates the video processing pipeline: transcript, LLM, embedding, and storage.

# Standard library imports
import os
import json
import time

# App imports
from app.videos.utils import extract_video_id
from app.videos.processor import fetch_transcript, process_transcript
from app.videos.embedder import process_json_file
from app.utils.redis_manager import redis_client
from app.utils.logger import get_logger


# Logger setup
logger = get_logger(__name__)

# Folder constants
TRANSCRIPTS_DIR = "app/data/transcripts"
PROCESSED_DIR = "app/data/processed_transcripts"
FORMATTED_DIR = "app/data/formatted_jsons"


def ensure_dirs():
    """
    Ensure all necessary folders exist before writing files.
    """
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FORMATTED_DIR, exist_ok=True)

def wait_for_valid_json(path, timeout=20, interval=1):
    """
    Wait until file contains valid JSON with key fields.
    Args:
        path (str): Path to JSON file
        timeout (int): Max seconds to wait
        interval (int): Poll interval in seconds
    Returns:
        bool: True if valid JSON found, else False
    """
    waited = 0
    while waited < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("videoTitle") and data.get("metadata"):
                        return True
            except json.JSONDecodeError:
                pass
        time.sleep(interval)
        waited += interval
    return False

def delete_intermediate_files(video_id):
    """
    Remove transient files if video processing failed.
    Args:
        video_id (str): YouTube video ID
    """
    for folder, ext in [
        (TRANSCRIPTS_DIR, ".txt"),
        (PROCESSED_DIR, ".json"),
        (FORMATTED_DIR, ".json")
    ]:
        path = os.path.join(folder, f"{video_id}{ext}")
        if os.path.exists(path):
            os.remove(path)


def run_video_pipeline(youtube_url: str):
    """
    Run the full video processing pipeline: transcript, LLM, embedding, and storage.
    Args:
        youtube_url (str): YouTube video URL
    Returns:
        dict or str: Final JSON string or error dict
    """
    video_id = extract_video_id(youtube_url)
    if not video_id:
        logger.error("Invalid YouTube URL")
        return {"error": "❌ Invalid YouTube URL"}

    ensure_dirs()
    logger.info(f"Starting pipeline for: {video_id}")

    redis_key = f"video:{video_id}"
    if redis_client.exists(redis_key):
        logger.warning(f"Video already exists in Redis: {redis_key}")
        return {"error": "⚠️ Video already exists in Redis."}

    try:
        transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.txt")

        # Phase 1: Fetch transcript
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            transcript = fetch_transcript(video_id)
            if not transcript or not transcript.strip():
                delete_intermediate_files(video_id)
                logger.warning(f"Empty transcript for {video_id}. Skipping.")
                return {"error": "⚠️ Empty transcript. Skipping."}

        # Phase 1: Process transcript
        result = process_transcript(video_id, transcript)
        if not result:
            delete_intermediate_files(video_id)
            logger.error(f"Phase 1 failed for {video_id}")
            return {"error": "❌ Phase 1 failed"}

        json_path = os.path.join(PROCESSED_DIR, f"{video_id}.json")
        if not wait_for_valid_json(json_path):
            delete_intermediate_files(video_id)
            logger.error(f"Processed JSON is invalid or incomplete for {video_id}")
            return {"error": "❌ Processed JSON is invalid or incomplete."}

        # Phase 2: Embedding
        process_json_file(json_path)

        # Final JSON
        formatted_path = os.path.join(FORMATTED_DIR, f"{video_id}.json")
        if os.path.exists(formatted_path):
            with open(formatted_path, "r", encoding="utf-8") as f:
                logger.info(f"Pipeline complete for {video_id}")
                return f.read()
        else:
            logger.error(f"Final JSON not found for {video_id}")
            return {"error": "❌ Final JSON not found."}

    except Exception as e:
        delete_intermediate_files(video_id)
        logger.error(f"Unexpected error for {video_id}: {str(e)}")
        return {"error": f"❌ Unexpected error: {str(e)}"}
