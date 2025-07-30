# Standard library imports
import os
import csv
import json
import re
import uuid
import shutil

# Third-party imports
import requests
from dotenv import load_dotenv
from typing import List, Tuple

# App imports
from app.utils.redis_manager import redis_client
from app.utils.logger import get_logger


logger = get_logger(__name__)

# In-memory normalized title index (populated at module load)
    # Removed in-memory normalized title index logic
    # _normalized_book_title_index = None
    # def _normalize_title_for_index(title: str) -> str:
    #     return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip()) if title else ''
    # def _build_normalized_book_title_index():
    #     index = {}
    #     for key in redis_client.scan_iter("book:*"):
    #         try:
    #             data = redis_client.json().get(key)
    #             if isinstance(data, dict):
    #                 title = data.get("book_title", "")
    #                 norm = _normalize_title_for_index(title)
    #                 if norm:
    #                     index[norm] = key
    #         except Exception:
    #             continue
    #     return index
    # def get_normalized_book_title_index():
    #     global _normalized_book_title_index
    #     if _normalized_book_title_index is None:
    #         _normalized_book_title_index = _build_normalized_book_title_index()
    #     return _normalized_book_title_index

load_dotenv()

# ----------------- ENV & Constants ----------------- #
DEEPNFRA_TOKEN = os.getenv("DEEPINFRA_TOKEN")
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
HEADERS = {"Authorization": f"Bearer {DEEPNFRA_TOKEN}"}

redis_json = redis_client.json()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploaded_books")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed_books")
FINAL_CSV_FOLDER = os.path.join(BASE_DIR, "data", "final_books_csv")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FINAL_CSV_FOLDER, exist_ok=True)

SEARCHABLE_COLUMNS = [
    "book_title",
    "dimension",
    "sub_themes",
    "audience",
    "difficulty",
    "tone_and_style",
    "length",
    "user_goal_alignment",
    "challenge_addressed",
    "stage_of_wellness_journey",
    "activity_engagement_compatibility",
    "conversational_keywords",
    "emotional_behavioral_triggers",
    "personality_fit",
    "recommended_complementary_resources"
]

# ----------------- Helpers ----------------- #
def to_snake_case(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'[\s\-]+', '_', text)
    text = re.sub(r'[^\w]', '', text)
    return text

def generate_uuid(title: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9]', '', title)[:6].lower() or "book"
    return f"{cleaned}_{uuid.uuid4()}"

def get_embedding(text: str) -> List[float] | None:
    """
    Get embedding for the given text using DeepInfra API. Logs errors if any.
    """
    try:
        resp = requests.post(
            "https://api.deepinfra.com/v1/openai/embeddings",
            headers=HEADERS,
            json={"model": EMBEDDING_MODEL, "input": [text]}
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None

def check_duplicate_by_title(book_title: str) -> bool:
    """
    Check for duplicate book by title using RediSearch text search (no in-memory index).
    Returns True if a book with the same normalized title exists, else False.
    """
    try:
        filtered_query = re.sub(r'[^a-zA-Z0-9 ]', '', book_title).strip().lower()
        query_str = re.sub(r'([@!{}()\[\]\|><"~*:\\])', r'\\\1', filtered_query)
        search_query = f'@book_title:{query_str}'
        args = [
            'book_idx',
            search_query,
            'LIMIT', '0', '1',
        ]
        res = redis_client.execute_command('FT.SEARCH', *args)
        # If any result found, it's a duplicate
        return bool(res and len(res) > 2)
    except Exception as e:
        logger.error(f"RediSearch error in duplicate check: {e}")
        return False

def build_searchable_text(row: dict[str, str]) -> str:
    return " ".join(str(row.get(col, "")) for col in SEARCHABLE_COLUMNS)

# ----------------------------- BOOKS PROCESSOR ----------------------------- #
# All duplicate detection and search now use RediSearch. No in-memory index logic remains.
# Functions are commented and logging is present for all major operations.
# ----------------- Main Entry ----------------- #
def process_book_csv(uploaded_file_path: str) -> Tuple[List[dict[str, str]], str]:
    """
    Process a CSV file containing book data, generate embeddings, and store in Redis.
    Logs all major actions and errors.
    """
    processed_books = []
    total, failed, duplicates = 0, 0, 0

    filename = os.path.basename(uploaded_file_path)
    saved_path = os.path.join(UPLOAD_FOLDER, filename)
    if uploaded_file_path != saved_path:
        shutil.copyfile(uploaded_file_path, saved_path)
        logger.info(f"Book CSV uploaded: {saved_path}")


    # Removed in-memory index refresh logic

    with open(saved_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            # Convert all keys to snake_case for consistency
            row_snake = {to_snake_case(k): v.strip() for k, v in row.items()}
            # Build row_data with all columns present in the row
            row_data = dict(row_snake)
            # Add normalized title for robust search (optional, not used in search now)
            def normalize_title(title):
                return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip())
            row_data["book_title_normalized"] = normalize_title(row_data.get("book_title", ""))
            # Build searchable_text as in the reference
            def stringify(value):
                if isinstance(value, list):
                    return ", ".join(map(str, value))
                return str(value) if value is not None else ""
            row_data["searchable_text"] = " ".join([stringify(row_data.get(col, '')) for col in SEARCHABLE_COLUMNS]).strip()

            # Require at least book_title and one other field to proceed
            if not row_data.get("book_title") or all(not v for k, v in row_data.items() if k != "book_title"):
                failed += 1
                logger.warning(f"Incomplete book data in row: {row}")
                continue

            if check_duplicate_by_title(row_data["book_title"]):
                duplicates += 1
                logger.info(f"Duplicate book found: {row_data['book_title']}")
                continue

            uuid_ = generate_uuid(row_data["book_title"])
            redis_key = f"book:{uuid_}"

            embedding = get_embedding(row_data["searchable_text"])
            if embedding is None:
                failed += 1
                logger.error(f"Failed to get embedding for book: {row_data['book_title']}")
                continue

            book_data = {
                "uuid": uuid_,
                **row_data,
                "embedding": embedding
            }

            redis_json.set(redis_key, "$", book_data)
            logger.info(f"Saved book to Redis: {redis_key}")

            json_path = os.path.join(PROCESSED_FOLDER, f"{uuid_}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(book_data, jf, indent=2, ensure_ascii=False)
            logger.info(f"Saved processed book JSON: {json_path}")

            processed_books.append(book_data)

    final_csv_path = os.path.join(FINAL_CSV_FOLDER, f"processed_books_{uuid.uuid4()}.csv")
    if processed_books:
        with open(final_csv_path, "w", encoding="utf-8", newline="") as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=processed_books[0].keys())
            writer.writeheader()
            writer.writerows(processed_books)
        logger.info(f"Saved processed books CSV: {final_csv_path}")

    summary = f"✅ Processed: {len(processed_books)} | ❌ Failed: {failed} | ⏭️ Duplicates: {duplicates} | 📊 Total: {total}"
    logger.info(summary)
    return processed_books, summary
