import os
import csv
import json
import re
import uuid
import shutil
import logging
import requests
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from redis.exceptions import ResponseError
from app.utils.redis_manager import redis_client

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
    try:
        resp = requests.post(
            "https://api.deepinfra.com/v1/openai/embeddings",
            headers=HEADERS,
            json={"model": EMBEDDING_MODEL, "input": [text]}
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logging.error(f"Embedding error: {e}")
        return None

def check_duplicate_by_title(book_title: str) -> bool:
    try:
        query = f"@book_title:'{book_title}'"
        result = redis_client.ft("book_idx").search(query)
        return result.total > 0
    except ResponseError:
        return False

def build_searchable_text(row: dict) -> str:
    return " ".join(str(row.get(col, "")) for col in SEARCHABLE_COLUMNS)

# ----------------- Main Entry ----------------- #
def process_book_csv(uploaded_file_path: str) -> Tuple[List[dict], str]:
    processed_books = []
    total, failed, duplicates = 0, 0, 0

    filename = os.path.basename(uploaded_file_path)
    saved_path = os.path.join(UPLOAD_FOLDER, filename)
    if uploaded_file_path != saved_path:
        shutil.copyfile(uploaded_file_path, saved_path)

    with open(saved_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            row_snake = {to_snake_case(k): v.strip() for k, v in row.items()}
            row_data = {col: row_snake.get(col, "") for col in SEARCHABLE_COLUMNS}

            if not all(row_data.values()):
                failed += 1
                continue

            if check_duplicate_by_title(row_data["book_title"]):
                duplicates += 1
                continue

            uuid_ = generate_uuid(row_data["book_title"])
            redis_key = f"book:{uuid_}"

            embedding = get_embedding(build_searchable_text(row_data))
            if embedding is None:
                failed += 1
                continue

            book_data = {
                "uuid": uuid_,
                **row_data,
                "embedding": embedding
            }

            redis_json.set(redis_key, "$", book_data)

            json_path = os.path.join(PROCESSED_FOLDER, f"{uuid_}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(book_data, jf, indent=2, ensure_ascii=False)

            processed_books.append(book_data)

    final_csv_path = os.path.join(FINAL_CSV_FOLDER, f"processed_books_{uuid.uuid4()}.csv")
    if processed_books:
        with open(final_csv_path, "w", encoding="utf-8", newline="") as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=processed_books[0].keys())
            writer.writeheader()
            writer.writerows(processed_books)

    summary = f"✅ Processed: {len(processed_books)} | ❌ Failed: {failed} | ⏭️ Duplicates: {duplicates} | 📊 Total: {total}"
    return processed_books, summary
