import os
import json
import time
from app.videos.utils import extract_video_id
from app.videos.processor import fetch_transcript, process_transcript
from app.videos.embedder import process_json_file
from app.redis_manager import RedisManager

r = RedisManager()

def ensure_dirs():
    """Ensure all necessary folders exist before writing files."""
    os.makedirs("app/data/transcripts", exist_ok=True)
    os.makedirs("app/data/processed_transcripts", exist_ok=True)
    os.makedirs("app/data/formatted_jsons", exist_ok=True)

def wait_for_valid_json(path, timeout=20, interval=1):
    """Wait until file contains valid JSON with key fields."""
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
    """Remove transient files if video processing failed."""
    for folder in ["app/data/transcripts", "app/data/processed_transcripts", "app/data/formatted_jsons"]:
        path = os.path.join(folder, f"{video_id}.txt" if "transcripts" in folder else f"{video_id}.json")
        if os.path.exists(path):
            os.remove(path)

def run_video_pipeline(youtube_url: str):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "❌ Invalid YouTube URL"}

    ensure_dirs()
    print(f"🎬 Starting pipeline for: {video_id}")

    redis_key = f"video:{video_id}"
    if r.exists(redis_key):
        return {"error": "⚠️ Video already exists in Redis."}

    try:
        transcript_path = os.path.join("app/data/transcripts", f"{video_id}.txt")

        # Phase 1: Fetch transcript
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            transcript = fetch_transcript(video_id)
            if not transcript.strip():
                delete_intermediate_files(video_id)
                return {"error": "⚠️ Empty transcript. Skipping."}

        # Phase 1: Process transcript
        result = process_transcript(video_id, transcript)
        if not result:
            delete_intermediate_files(video_id)
            return {"error": "❌ Phase 1 failed"}

        json_path = os.path.join("app/data/processed_transcripts", f"{video_id}.json")
        if not wait_for_valid_json(json_path):
            delete_intermediate_files(video_id)
            return {"error": "❌ Processed JSON is invalid or incomplete."}

        # Phase 2: Embedding
        process_json_file(json_path)

        # Final JSON
        formatted_path = os.path.join("app/data/formatted_jsons", f"{video_id}.json")
        if os.path.exists(formatted_path):
            with open(formatted_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return {"error": "❌ Final JSON not found."}

    except Exception as e:
        delete_intermediate_files(video_id)
        return {"error": f"❌ Unexpected error: {str(e)}"}
