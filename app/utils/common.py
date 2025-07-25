# Standard library imports
import re
import json
from typing import List, Dict, Any
# App imports
from app.redis_manager import RedisManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
redis = RedisManager()

def search_video_by_url_or_title(query: str) -> List[Dict[str, Any]]:
    """
    Search for video in Redis by URL or title.
    Returns list of matching video records.
    """
    results = []
    try:
        # Scan all video keys (for simplicity, can be optimized with RediSearch)
        for key in redis.client.scan_iter("video:*"):
            data = redis.get_json(key)
            if not data:
                continue
            # Match by URL or title (case-insensitive)
            if query.lower() in data.get("link", "").lower() or query.lower() in data.get("youtube_title", "").lower():
                results.append(data)
        logger.info(f"Search for '{query}' returned {len(results)} results.")
        return results
    except Exception as e:
        logger.error(f"Error during video search: {e}")
        return []

def search_book_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Search for book in Redis by name (to be implemented).
    """
    # ...future implementation...
    return []

def delete_by_key(key: str) -> bool:
    """
    Delete data in Redis by key.
    """
    try:
        if redis.exists(key):
            redis.client.delete(key)
            logger.info(f"Deleted key: {key}")
            return True
        else:
            logger.warning(f'Key not found for deletion: {key}')
            return False
    except Exception as e:
        logger.error(f"Error during deletion: {e}")
        return False

def escape_redisearch_query(query: str) -> str:
    """
    Escape special characters in query for RediSearch.
    For URLs and video IDs, we need to be extra careful with special characters.
    """
    query = query.strip()
    special_chars = ',.<>{}[]"\':;!@#$%^&*()-+=~/'
    escaped = ""
    for char in query:
        if char in special_chars:
            escaped += f"\\{char}"
        else:
            escaped += char
    print(f"[VideoSearch] Original query: {query}")
    print(f"[VideoSearch] Escaped query: {escaped}")
    return escaped

def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    Args:
        url (str): YouTube URL
    Returns:
        str: Video ID or empty string if not found
    """
    try:
        url = url.strip()
        patterns = [
            r"(?:v=|youtu.be/)([^&\?]+)",
            r"(?:embed/)([^&\?]+)",
            r"(?:watch\?v=)([^&\?]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                print(f"[VideoSearch] Extracted video ID: {video_id} from URL: {url}")
                return video_id
                
        # If the input looks like a video ID itself, return it
        if re.match(r'^[A-Za-z0-9_-]+$', url) and len(url) > 8:
            print(f"[VideoSearch] Input appears to be a video ID: {url}")
            return url
            
        print(f"[VideoSearch] Could not extract video ID from: {url}")
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting video ID: {e}")
        return ""

def hybrid_search_videos(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Perform similarity search for videos based on URL or title.
    First tries exact match by video ID (if URL provided),
    then performs semantic similarity search using embeddings.
    
    Args:
        query (str): Video URL or title to search for
        top_k (int): Number of top results to return
    Returns:
        list[dict]: List of dicts with redis_key, score, and data
    """
    print(f"[VideoSearch] Starting search for videos with query: '{query}'")
    if not query:
        print("[VideoSearch] Empty query, returning no results")
        return []

    try:
        results = []
        # Check if query is a YouTube URL
        video_id = extract_video_id(query)
        if video_id:
            # Try exact match by video ID first
            escaped_id = escape_redisearch_query(video_id)
            exact_query = f'@youtube_id:"{escaped_id}"'
            print(f"[VideoSearch] Trying exact match by video ID: {exact_query}")
            exact_results = hybrid_search('video_idx', exact_query, 1)
            
            if exact_results:
                print("[VideoSearch] Found exact match by video ID")
                video = exact_results[0]
                redis_key = video.get('redis_key', '')
                if not redis_key.startswith('video:'):
                    redis_key = f"video:{redis_key}"
                results.append({
                    'redis_key': redis_key,
                    'score': 1.0,  # Exact match gets highest score
                    'data': video,
                    'match_type': 'exact'
                })
                return results

        # Generate embedding for similarity search
        print("[VideoSearch] Generating query embedding")
        query_emb = _get_embedding(query, is_book=False)
        if not query_emb:
            print("[VideoSearch] Failed to generate query embedding")
            return []
            
        # Perform vector similarity search
        print("[VideoSearch] Performing vector similarity search")
        vector_results = vector_search('video_idx', query_emb, top_k)
        
        if vector_results:
            # Process vector search results
            for result in vector_results:
                redis_key = result.get('redis_key', '')
                if not redis_key.startswith('video:'):
                    redis_key = f"video:{redis_key}"
                # Skip if we already have this result from exact match
                if not any(r['redis_key'] == redis_key for r in results):
                    score = float(result.get('score', 0.0))
                    results.append({
                        'redis_key': redis_key,
                        'score': score,
                        'data': result.get('data', {}),
                        'match_type': 'similar'
                    })

        if not results:
            print("[VideoSearch] No results found")
            return []
            
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        final_results = results[:top_k]
        
        # Log results
        for r in final_results:
            print(f"[VideoSearch] Found {r['match_type']} match: {r['redis_key']} (score: {r['score']})")
            
        return final_results
        
    except Exception as e:
        print(f"[VideoSearch] Error during search: {str(e)}")
        return [] 
    

def hybrid_search_books(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Perform similarity search for books based on title/author.
    Uses vector similarity search to find semantically similar books.
    
    Args:
        query (str): The search query (book title, author, etc.)
        top_k (int): Number of top results to return
    Returns:
        list[dict]: List of dicts with redis_key, score, and data
    """
    print(f"[BookSearch] Starting search for books with query: '{query}'")
    if not query:
        print("[BookSearch] Empty query, returning no results")
        return []

    try:
        # Generate embedding for the query
        print("[BookSearch] Generating query embedding")
        query_emb = _get_embedding(query, is_book=True)
        if not query_emb:
            print("[BookSearch] Failed to generate query embedding")
            return []
            
        # Perform vector similarity search
        print("[BookSearch] Performing vector similarity search")
        results = vector_search('book_idx', query_emb, top_k)
        
        if not results:
            print("[BookSearch] No results found")
            return []
            
        # Log results
        for r in results:
            print(f"[BookSearch] Found match: {r['redis_key']} (score: {r['score']})")
            
        return results
        
    except Exception as e:
        print(f"[BookSearch] Error during search: {str(e)}")
        return []

# Stub for undefined functions

def hybrid_search():
    """Stub for hybrid_search."""
    return []

def _get_embedding():
    """Stub for embedding function."""
    return [0.0] * 768

def vector_search():
    """Stub for vector search function."""
    return []