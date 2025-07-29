
# Standard library imports
import re
from typing import List, Tuple, Any, Optional

# Third-party imports
from rapidfuzz import process
import redis.exceptions

# App imports
from app.utils.redis_manager import redis_client
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

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

        redis_client.delete(key)
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

def search_book_by_title(title_query: str) -> Tuple[List[str], List[Any]]:
    """
    Search books by title using RediSearch with fallback to fuzzy search.

    Returns empty lists with message if no results found.
    """
    try:
        # Use the book_title field directly (no normalization)
        query_escaped = escape_query_string(title_query)
        # Additionally escape double quotes for phrase queries
        query_escaped = query_escaped.replace('"', '\"')
        if ' ' in title_query.strip():
            # Exact phrase match on book_title, ensure quotes are escaped
            query = f'@book_title:"{query_escaped}"'
        else:
            # Prefix/wildcard match on book_title
            query = f'@book_title:{query_escaped}*'
        result = redis_client.ft("book_idx").search(query)
        docs = getattr(result, 'docs', [])
        matches = []
        for doc in docs:
            doc_id = getattr(doc, 'id', None)
            if doc_id:
                data = redis_client.json().get(doc_id)
                matches.append((doc_id, data))
    except (redis.exceptions.ResponseError, AttributeError) as e:
        logger.warning(f"RedisSearch failed on book_idx: {e}")
        # Fallback to fuzzy search
        all_keys = list(redis_client.scan_iter("book:*"))
        all_data = []
        for key in all_keys:
            try:
                data = redis_client.json().get(key)
                # Defensive: data may be None or a list
                title = ""
                if isinstance(data, dict):
                    title = data.get("book_title", "")
                all_data.append((key, title, data))
            except Exception:
                continue

        best_matches = process.extract(title_query, [t[1] for t in all_data], limit=5, score_cutoff=40)
        match_titles = {m[0] for m in best_matches}
        matches = [(key, data) for key, title, data in all_data if title in match_titles]

    if not matches:
        logger.info(f"No book results found for query: {title_query}")
        return [], [{"message": f"❌ No related book results found for: '{title_query}'"}]

    keys = [k for k, _ in matches]
    data = [d for _, d in matches]
    return keys, data

# ----------------------------- VIDEO SEARCH ----------------------------- #

def extract_video_id(url_or_text: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL or plain text.

    Args:
        url_or_text (str): YouTube URL or title.

    Returns:
        str: Extracted video ID (if found), else None.
    """
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url_or_text)
    return match.group(1) if match else None

def search_video_by_title_or_url(input_text: str) -> Tuple[List[str], List[Any]]:
    """
    Search videos by URL (direct key lookup) or title (RediSearch/fuzzy).

    Returns empty list with message if nothing found.
    """

    video_id = extract_video_id(input_text)
    if video_id:
        key = f"video:{video_id}"
        try:
            data = redis_client.json().get(key)
            if data:
                return [key], [data]
        except redis.exceptions.ResponseError as e:
            logger.error(f"Error fetching video key {key}: {e}")
        return [], [{"message": f"❌ No related video found for ID: '{video_id}'"}]

    # Title search
    def normalize_for_search(text):
        return re.sub(r'[^a-zA-Z0-9 ]', '', text.lower().strip())

    try:
        # Try direct RediSearch with normalized query
        norm_query = normalize_for_search(input_text)
        query_escaped = escape_query_string(norm_query)
        if ' ' in norm_query:
            query = f'@youtube_title:"{query_escaped}"'
        else:
            query = f'@youtube_title:{query_escaped}*'
        result = redis_client.ft("video_idx").search(query)
        docs = getattr(result, 'docs', [])
        matches = []
        for doc in docs:
            doc_id = getattr(doc, 'id', None)
            if doc_id:
                data = redis_client.json().get(doc_id)
                matches.append((doc_id, data))
        # If no matches, fallback to fuzzy search
        if not matches:
            raise ValueError('No direct RediSearch match, fallback to fuzzy')
    except (redis.exceptions.ResponseError, AttributeError, ValueError) as e:
        logger.warning(f"RedisSearch failed on video_idx: {e}")
        # Fuzzy fallback
        all_keys = list(redis_client.scan_iter("video:*"))
        all_data = []
        for key in all_keys:
            try:
                data = redis_client.json().get(key)
                title = ""
                if isinstance(data, dict):
                    title = data.get("youtube_title", "")
                all_data.append((key, title, data))
            except Exception:
                continue

        best_matches = process.extract(input_text, [t[1] for t in all_data], limit=5, score_cutoff=40)
        match_titles = {m[0] for m in best_matches}
        matches = [(key, data) for key, title, data in all_data if title in match_titles]

    if not matches:
        logger.info(f"No video results found for query: {input_text}")
        return [], [{"message": f"❌ No related video results found for: '{input_text}'"}]

    keys = [k for k, _ in matches]
    data = [d for _, d in matches]
    return keys, data

def normalize_title(title):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip())
