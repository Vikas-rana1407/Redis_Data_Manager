# Standard library imports
import re
from typing import List, Tuple, Any, Optional
import numpy as np

# Third-party imports
import redis.exceptions

# App imports
from app.utils.redis_manager import redis_client
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# ----------------------------- CONSTANTS ----------------------------- #
FT_SEARCH_CMD = 'FT.SEARCH'

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

def filter_search_term(term: str) -> str:
    """
    Remove special characters and extra whitespace from search term for robust RediSearch matching.
    """
    return re.sub(r'[^a-zA-Z0-9 ]', '', term).strip().lower()

# ----------------------------- BOOK SEARCH ----------------------------- #

def search_book_by_title(title_query: str) -> Tuple[List[str], List[Any]]:
    """
    Search books by title using RediSearch text search (case/punctuation-insensitive).

    Returns empty lists with message if no results found.
    """
    try:
        # Filter and normalize query for RediSearch
        filtered_query = filter_search_term(title_query)
        query_str = escape_query_string(filtered_query)
        # Use fuzzy or prefix search if desired, e.g. '%query%'
        search_query = f'@book_title:{query_str}'
        args = [
            'book_idx',
            search_query,
            'RETURN', '2', '__key__', 'book_title',
            'LIMIT', '0', '10',
        ]
        logger.info(f"FT.SEARCH args: {args}")
        res = redis_client.execute_command(FT_SEARCH_CMD, *args)
        logger.info(f"FT.SEARCH raw response: {res}")
        if not res or len(res) < 2:
            logger.info(f"No book results found for query: {title_query}")
            return [], [{"message": f"❌ No book results found for: '{title_query}'"}]
        keys = []
        data = []
        for i in range(1, len(res), 2):
            key = res[i]
            full_data = redis_client.json().get(key)
            if full_data:
                keys.append(key)
                data.append(full_data)
        logger.info(f"Found {len(keys)} book results for query: {title_query}")
        return keys, data
    except Exception as e:
        logger.error(f"RediSearch error: {e}")
        return [], [{"message": f"❌ Error searching books with RediSearch: {e}"}]

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
    Search videos by URL (direct key lookup) or RediSearch text search by title.

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
    try:
        filtered_query = filter_search_term(input_text)
        query_str = escape_query_string(filtered_query)
        search_query = f'@youtube_title:{query_str}'
        args = [
            'video_idx',
            search_query,
            'RETURN', '2', '__key__', 'youtube_title',
            'LIMIT', '0', '10',
        ]
        logger.info(f"FT.SEARCH args: {args}")
        res = redis_client.execute_command(FT_SEARCH_CMD, *args)
        logger.info(f"FT.SEARCH raw response: {res}")
        if not res or len(res) < 2:
            return [], [{"message": f"❌ No video results found for: '{input_text}'"}]
        keys = []
        data = []
        for i in range(1, len(res), 2):
            key = res[i]
            # Fetch full JSON for each key
            full_data = redis_client.json().get(key)
            if full_data:
                keys.append(key)
                data.append(full_data)
        return keys, data
    except Exception as e:
        logger.error(f"RediSearch error: {e}")
        return [], [{"message": f"❌ Error searching videos with RediSearch: {e}"}]

def normalize_title(title: str) -> str:
    """
    Normalize a title by removing special characters and converting to lowercase.
    """
    return re.sub(r'[^a-zA-Z0-9 ]', '', title).strip().lower()

# ----------------------------- BOOK DUPLICATE CHECK ----------------------------- #

def check_duplicate_by_title(title: str) -> bool:
    """
    Check for duplicate book by title using RediSearch text search (case/punctuation-insensitive).
    Returns True if duplicate exists, False otherwise.
    """
    try:
        filtered_title = filter_search_term(title)
        query_str = escape_query_string(filtered_title)
        search_query = f'@book_title:{query_str}'
        args = [
            'book_idx',
            search_query,
            'LIMIT', '0', '1',
        ]
        logger.info(f"FT.SEARCH args for duplicate check: {args}")
        res = redis_client.execute_command(FT_SEARCH_CMD, *args)
        logger.info(f"FT.SEARCH raw response for duplicate check: {res}")
        is_duplicate = bool(res and len(res) > 1)
        logger.info(f"Duplicate book found: {is_duplicate}")
        return is_duplicate
    except Exception as e:
        logger.error(f"RediSearch error in duplicate check: {e}")
        return False

# ----------------------------- VIDEO DUPLICATE CHECK ----------------------------- #

def check_duplicate_by_video_title(title: str) -> bool:
    """
    Check for duplicate video by title using RediSearch text search (case/punctuation-insensitive).
    Returns True if duplicate exists, False otherwise.
    """
    try:
        filtered_title = filter_search_term(title)
        query_str = escape_query_string(filtered_title)
        search_query = f'@video_title:{query_str}'
        args = [
            'video_idx',
            search_query,
            'LIMIT', '0', '1',
        ]
        logger.info(f"FT.SEARCH args for video duplicate check: {args}")
        result = redis_client.execute_command(FT_SEARCH_CMD, *args)
        logger.info(f"FT.SEARCH raw response for video duplicate check: {result}")
        is_duplicate = bool(result and len(result) > 1)
        logger.info(f"Duplicate video found: {is_duplicate}")
        return is_duplicate
    except Exception as e:
        logger.error(f"RediSearch error in video duplicate check: {e}")
        return False
