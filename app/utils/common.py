# In-memory normalized video title index for search
_normalized_video_title_index = None

def _normalize_video_title_for_index(title: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip()) if title else ''

def _build_normalized_video_title_index():
    index = {}
    for key in redis_client.scan_iter("video:*"):
        try:
            data = redis_client.json().get(key)
            if isinstance(data, dict):
                title = data.get("youtube_title", "")
                norm = _normalize_video_title_for_index(title)
                if norm:
                    index[norm] = (key, data)
        except Exception:
            continue
    return index

def get_normalized_video_title_index():
    global _normalized_video_title_index
    if _normalized_video_title_index is None:
        _normalized_video_title_index = _build_normalized_video_title_index()
    return _normalized_video_title_index
# In-memory normalized book title index for search
_normalized_book_title_index = None

def _normalize_title_for_index(title: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip()) if title else ''

def _build_normalized_book_title_index():
    index = {}
    for key in redis_client.scan_iter("book:*"):
        try:
            data = redis_client.json().get(key)
            if isinstance(data, dict):
                title = data.get("book_title", "")
                norm = _normalize_title_for_index(title)
                if norm:
                    index[norm] = (key, data)
        except Exception:
            continue
    return index

def get_normalized_book_title_index():
    global _normalized_book_title_index
    if _normalized_book_title_index is None:
        _normalized_book_title_index = _build_normalized_book_title_index()
    return _normalized_book_title_index

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
    # Use in-memory normalized index for robust, fast search
    norm_query = _normalize_title_for_index(title_query)
    index = get_normalized_book_title_index()
    matches = []
    if norm_query in index:
        key, data = index[norm_query]
        matches.append((key, data))
    else:
        # Fallback: fuzzy match on normalized titles
        from rapidfuzz import process
        all_norm_titles = list(index.keys())
        best_matches = process.extract(norm_query, all_norm_titles, limit=5, score_cutoff=60)
        match_norms = {m[0] for m in best_matches}
        matches = [index[n] for n in match_norms if n in index]

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

    # Title search using in-memory normalized index
    norm_query = _normalize_video_title_for_index(input_text)
    index = get_normalized_video_title_index()
    matches = []
    if norm_query in index:
        key, data = index[norm_query]
        matches.append((key, data))
    else:
        # Fuzzy fallback on normalized titles
        from rapidfuzz import process
        all_norm_titles = list(index.keys())
        best_matches = process.extract(norm_query, all_norm_titles, limit=5, score_cutoff=60)
        match_norms = {m[0] for m in best_matches}
        matches = [index[n] for n in match_norms if n in index]

    if not matches:
        logger.info(f"No video results found for query: {input_text}")
        return [], [{"message": f"❌ No related video results found for: '{input_text}'"}]

    keys = [k for k, _ in matches]
    data = [d for _, d in matches]
    return keys, data

def normalize_title(title):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', title.lower().strip())
