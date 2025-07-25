# app/videos/embbeder.py

import os
import json
import logging
import requests
import redis
from dotenv import load_dotenv
from app.videos.utils import stringify

load_dotenv()

# Constants
INPUT_DIR = "app/data/processed_transcripts"
OUTPUT_DIR = "app/data/formatted_jsons"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

REDIS_URL = os.getenv("REDIS_URL")
DEEPINFRA_TOKEN = os.getenv("DEEPINFRA_TOKEN")
redis_client = redis.from_url(REDIS_URL, decode_responses=False)
redis_json = redis_client.json()

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_embedding(text: str):
    try:
        resp = requests.post(
            "https://api.deepinfra.com/v1/openai/embeddings",
            headers={"Authorization": f"Bearer {DEEPINFRA_TOKEN}"},
            json={"model": EMBEDDING_MODEL, "input": [text]}
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logging.error(f"❌ Embedding failed: {e}")
        return None

def build_searchable_text(fields):
    return " ".join([stringify(f) for f in fields if f]).strip()

def process_json_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        video_id = data.get("videoId")
        if not video_id:
            print(f"⚠️ Missing videoId in {filepath}")
            return

        redis_key = f"video:{video_id}"
        if redis_client.exists(redis_key):
            print(f"⏭️ Already in Redis: {redis_key}")
            return

        metadata = data.get("metadata", {})
        classification = metadata.get("classification", {})
        tags = metadata.get("contextualTags", {})

        searchable_text = build_searchable_text([
            data.get("videoTitle", ""),
            classification.get("primaryCategory"),
            classification.get("secondaryCategory"),
            classification.get("activityType"),
            classification.get("goalObjective"),
            tags.get("duration")
        ])

        embedding = get_embedding(searchable_text)
        if not embedding:
            return

        final_json = {
            "youtube_title": data.get("videoTitle", ""),
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "duration": tags.get("duration"),
            "ai_duration": tags.get("duration"),
            "primaryCategory": classification.get("primaryCategory", ""),
            "secondaryCategory": stringify(classification.get("secondaryCategory", "")),
            "activityType": classification.get("activityType", ""),
            "goalObjective": classification.get("goalObjective", ""),
            "userExperience": tags.get("userExperience"),
            "intensity": tags.get("intensity"),
            "searchable_text": searchable_text,
            "embedding": embedding,
        }

        with open(os.path.join(OUTPUT_DIR, f"{video_id}.json"), "w", encoding="utf-8") as f:
            json.dump(final_json, f, indent=4)

        redis_json.set(redis_key, "$", final_json)
        print(f"✅ Stored in Redis: {redis_key}")

    except Exception as e:
        logging.error(f"❌ Error processing {filepath}: {e}")
