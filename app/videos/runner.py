# app/videos/runner.py

import os
from app.videos.utils import extract_video_id
from app.videos.processor import fetch_transcript, process_transcript
from app.videos.embedder import process_json_file

def run_video_pipeline(youtube_url: str):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "❌ Invalid YouTube URL"}

    print(f"🎬 Starting pipeline for: {video_id}")
    transcript_path = os.path.join("app/data/transcripts", f"{video_id}.txt")

    # Phase 1
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = fetch_transcript(video_id)

    result = process_transcript(video_id, transcript)
    if not result:
        return {"error": "❌ Phase 1 failed"}

    # Phase 2
    json_path = os.path.join("app/data/processed_transcripts", f"{video_id}.json")
    process_json_file(json_path)

    return result
