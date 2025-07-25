import os
import json
import time
from app.videos.utils import extract_video_id
from app.videos.processor import fetch_transcript, process_transcript
from app.videos.embedder import process_json_file

def wait_for_valid_json(path, timeout=20, interval=1):
    """Wait until file contains valid JSON with key fields"""
    waited = 0
    while waited < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("videoTitle") and data.get("metadata"):
                        return True
            except json.JSONDecodeError:
                pass  # Try again on next interval
        time.sleep(interval)
        waited += interval
    return False

def run_video_pipeline(youtube_url: str):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "❌ Invalid YouTube URL"}

    print(f"🎬 Starting pipeline for: {video_id}")
    transcript_path = os.path.join("app/data/transcripts", f"{video_id}.txt")

    # Phase 1: Fetch & Process Transcript
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = fetch_transcript(video_id)

    result = process_transcript(video_id, transcript)
    if not result:
        return {"error": "❌ Phase 1 failed"}

    # Wait for valid processed JSON
    json_path = os.path.join("app/data/processed_transcripts", f"{video_id}.json")
    if not wait_for_valid_json(json_path):
        return {"error": "❌ Processed JSON is invalid or incomplete."}

    # Phase 2: Embed and Save
    process_json_file(json_path)

    # Return final JSON
    formatted_path = os.path.join("app/data/formatted_jsons", f"{video_id}.json")
    if os.path.exists(formatted_path):
        with open(formatted_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return {"error": "❌ Final JSON not found."}
