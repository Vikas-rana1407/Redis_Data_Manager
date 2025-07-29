import logging
import re
import json
from typing import List, Tuple
from rapidfuzz import process
from app.redis_manager import RedisManager
import redis.exceptions

logger = logging.getLogger(__name__)
redis_client = RedisManager()

# ----------------------------- DELETE LOGIC ----------------------------- #

def delete_multiple_keys(keys: str, expected_prefix: str) -> str:
    """
    Delete multiple Redis keys. Validates each key and returns status messages.

    Args:
        keys (str): Comma-separated Redis keys.
        expected_prefix (str): 'book:' or 'video:' to validate prefix.

    Returns:
        str: Multiline status messages for each key.
    """
    key_list = [key.strip() for key in keys.split(",") if key.strip()]
    if not key_list:
        return "⚠️ No keys provided."

    messages = []
    for key in key_list:
        if not key.startswith(expected_prefix):
            messages.append(f"❌ '{key}': Key must start with `{expected_prefix}`")
            continue

        if not redis_client.exists(key):
            messages.append(f"⚠️ '{key}': Key does not exist.")
            continue

        redis_client.client.delete(key)
        logger.info(f"✅ Deleted Redis key: {key}")
        messages.append(f"✅ '{key}': Successfully deleted.")

    return "\n".join(messages)

# ----------------------------- UTILITY ----------------------------- #

def escape_query_string(text: str) -> str:
    """
    Escape special characters for RediSearch query.

    Args:
        text (str): Raw user input.

    Returns:
        str: Escaped query string.
    """
    return re.sub(r'([@!{}()\[\]\|><"~*:\\])', r'\\\1', text)

# ----------------------------- BOOK SEARCH ----------------------------- #

def search_book_by_title(title_query: str) -> Tuple[List[str], List[dict]]:
    """
    Search books by title using RediSearch with fallback to fuzzy search.

    Returns empty lists with message if no results found.
    """
    try:
        escaped_query = escape_query_string(title_query)
        query = f'@book_title:"{escaped_query}*"'
        result = redis_client.client.ft("book_idx").search(query)
        matches = [(doc.id, redis_client.client.json().get(doc.id)) for doc in result.docs]
    except (redis.exceptions.ResponseError, AttributeError) as e:
        logger.warning(f"RedisSearch failed on book_idx: {e}")
        # Fallback to fuzzy search
        all_keys = list(redis_client.client.scan_iter("book:*"))
        all_data = []
        for key in all_keys:
            try:
                data = redis_client.client.json().get(key)
                title = data.get("book_title", "")
                all_data.append((key, title, data))
            except Exception:
                continue

        best_matches = process.extract(title_query, [t[1] for t in all_data], limit=5, score_cutoff=40)
        matches = [(key, data) for key, title, data in all_data if title in dict(best_matches)]

    if not matches:
        logger.info(f"No book results found for query: {title_query}")
        return [], [{"message": f"❌ No related book results found for: '{title_query}'"}]

    keys = [k for k, _ in matches]
    data = [d for _, d in matches]
    return keys, data

# ----------------------------- VIDEO SEARCH ----------------------------- #

def extract_video_id(url_or_text: str) -> str:
    """
    Extract YouTube video ID from URL or plain text.

    Args:
        url_or_text (str): YouTube URL or title.

    Returns:
        str: Extracted video ID (if found), else None.
    """
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url_or_text)
    return match.group(1) if match else None

def search_video_by_title_or_url(input_text: str) -> Tuple[List[str], List[dict]]:
    """
    Search videos by URL (direct key lookup) or title (RediSearch/fuzzy).

    Returns empty list with message if nothing found.
    """
    video_id = extract_video_id(input_text)
    if video_id:
        key = f"video:{video_id}"
        try:
            data = redis_client.client.json().get(key)
            if data:
                return [key], [data]
        except redis.exceptions.ResponseError as e:
            logger.error(f"Error fetching video key {key}: {e}")
        return [], [{"message": f"❌ No related video found for ID: '{video_id}'"}]

    # Title search
    try:
        escaped_query = escape_query_string(input_text)
        query = f'@youtube_title:"{escaped_query}*"'
        result = redis_client.client.ft("video_idx").search(query)
        matches = [(doc.id, redis_client.client.json().get(doc.id)) for doc in result.docs]
    except (redis.exceptions.ResponseError, AttributeError) as e:
        logger.warning(f"RedisSearch failed on video_idx: {e}")
        # Fuzzy fallback
        all_keys = list(redis_client.client.scan_iter("video:*"))
        all_data = []
        for key in all_keys:
            try:
                data = redis_client.client.json().get(key)
                title = data.get("youtube_title", "")
                all_data.append((key, title, data))
            except Exception:
                continue

        best_matches = process.extract(input_text, [t[1] for t in all_data], limit=5, score_cutoff=40)
        matches = [(key, data) for key, title, data in all_data if title in dict(best_matches)]

    if not matches:
        logger.info(f"No video results found for query: {input_text}")
        return [], [{"message": f"❌ No related video results found for: '{input_text}'"}]

    keys = [k for k, _ in matches]
    data = [d for _, d in matches]
    return keys, data

def normalize_title(title):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip())
