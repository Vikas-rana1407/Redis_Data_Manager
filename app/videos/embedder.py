import os
import json
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from app.redis_manager import RedisManager
from dotenv import load_dotenv
import yt_dlp
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()

# Constants
DEEPINFRA_TOKEN = os.getenv('DEEPINFRA_TOKEN')
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), '../data/processed_transcripts')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../data/formatted_jsons')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
NUM_THREADS = 20

class VideoEmbedder:
    """
    Handles embedding and batch processing of processed video transcripts:
    - Generate embeddings for searchable text
    - Format and save enhanced data to Redis
    - Batch process all processed transcripts
    """
    def __init__(self):
        """Initialize VideoEmbedder with Redis manager and progress tracking."""
        self.redis = RedisManager()
        self.progress_lock = Lock()
        self.progress_count = 0

    def stringify(self, value):
        """Convert list to comma-separated string."""
        return ", ".join(map(str, value)) if isinstance(value, list) else str(value or "")

    def get_youtube_duration_seconds(self, video_url):
        """Fetch video duration using yt_dlp."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'nocache': True, 'skip_download': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get("duration", None)
        except Exception as e:
            logger.warning(f"❌ Duration fetch failed for {video_url}: {e}")
            return None

    def get_embedding(self, text):
        """Get embedding for text using DeepInfra API."""
        try:
            resp = requests.post(
                "https://api.deepinfra.com/v1/openai/embeddings",
                headers={"Authorization": f"Bearer {DEEPINFRA_TOKEN}"},
                json={"model": EMBEDDING_MODEL, "input": [text]}
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Failed to get embedding: {e} | Text: {text[:60]}")
            return None

    def build_searchable_text(self, fields):
        """Build searchable text from relevant fields."""
        return " ".join([self.stringify(f) for f in fields]).strip()

    def process_json_file(self, filepath):
        """Process a single processed transcript file: embed, format, save to Redis."""
        try:
            filename = os.path.basename(filepath)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            video_id = data.get("videoId")
            if not video_id:
                logger.warning(f"⚠️ Missing videoId: {filename}")
                return
            redis_key = f"video:{video_id}"
            if self.redis.exists(redis_key):
                logger.info(f"⏭️ Already exists in Redis: {redis_key}")
                return
            youtube_title = data.get("videoTitle", "")
            link = f"https://www.youtube.com/watch?v={video_id}"
            duration = self.get_youtube_duration_seconds(link)
            metadata = data.get("metadata", {})
            classification = metadata.get("classification", {})
            tags = metadata.get("contextualTags", {})
            ai_duration = tags.get("duration")
            searchable_text = self.build_searchable_text([
                youtube_title,
                classification.get("primaryCategory", ""),
                classification.get("secondaryCategory", []),
                classification.get("activityType", ""),
                classification.get("goalObjective", ""),
                ai_duration
            ])
            embedding = self.get_embedding(searchable_text)
            if not embedding:
                logger.warning(f"❌ Embedding failed: {filename}")
                return
            final_json = {
                "youtube_title": youtube_title,
                "link": link,
                "duration": duration,
                "ai_duration": ai_duration,
                "primaryCategory": classification.get("primaryCategory", ""),
                "secondaryCategory": self.stringify(classification.get("secondaryCategory", "")),
                "activityType": classification.get("activityType", ""),
                "goalObjective": classification.get("goalObjective", ""),
                "userExperience": tags.get("userExperience"),
                "intensity": tags.get("intensity"),
                "searchable_text": searchable_text,
                "embedding": embedding
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_json, f, indent=4)
            self.redis.set_json(redis_key, final_json)
            logger.info(f"✅ Stored in Redis: {redis_key}")
        except Exception as e:
            logger.error(f"❌ Error in {filepath}: {e}\n{traceback.format_exc()}")
        finally:
            with self.progress_lock:
                self.progress_count += 1
                print(f"\rProcessed: {self.progress_count}", end='', flush=True)

    def process_all(self):
        """Batch process all processed transcript files."""
        files = [
            os.path.join(PROCESSED_FOLDER, f)
            for f in os.listdir(PROCESSED_FOLDER)
            if f.endswith(".json")
        ]
        logger.info(f"🎯 Found {len(files)} files | Threads: {NUM_THREADS}")
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            executor.map(self.process_json_file, files)
        print("\n✅ All files processed.")
