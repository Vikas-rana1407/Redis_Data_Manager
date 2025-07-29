
# app/videos/embedder.py
# Embeds processed video JSONs, stores in Redis, and logs all actions.

# Standard library imports
import os
import json

# Third-party imports
import requests
import redis
from dotenv import load_dotenv

# App imports
from app.videos.utils import stringify
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# Load environment variables
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
    """
    Get embedding vector for input text using DeepInfra API.
    Args:
        text (str): Input text
    Returns:
        list or None: Embedding vector if successful, else None
    """
    try:
        resp = requests.post(
            "https://api.deepinfra.com/v1/openai/embeddings",
            headers={"Authorization": f"Bearer {DEEPINFRA_TOKEN}"},
            json={"model": EMBEDDING_MODEL, "input": [text]}
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None

def build_searchable_text(fields):
    """
    Build a single string from multiple fields for embedding/search.
    Args:
        fields (list): List of fields (str or list)
    Returns:
        str: Concatenated searchable text
    """
    return " ".join([stringify(f) for f in fields if f]).strip()

def process_json_file(filepath):
    """
    Process a single processed_transcripts JSON file: embed, store in Redis, and log actions.
    Args:
        filepath (str): Path to processed JSON file
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        video_id = data.get("videoId")
        if not video_id:
            logger.warning(f"Missing videoId in {filepath}")
            return

        redis_key = f"video:{video_id}"
        if redis_client.exists(redis_key):
            logger.info(f"Already in Redis: {redis_key}")
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
            logger.error(f"Embedding failed for {filepath}")
            return


        def normalize_title(title):
            import re
            return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip())

        final_json = {
            "youtube_title": data.get("videoTitle", ""),
            "youtube_title_normalized": normalize_title(data.get("videoTitle", "")),
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
        logger.info(f"Stored in Redis: {redis_key}")

    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
