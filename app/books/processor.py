# Standard library imports
import os
from typing import List, Dict, Any

# Third-party imports
import pandas as pd

# App imports
from app.utils.logger import get_logger
from app.redis_manager import RedisManager
from app.videos.embedder import VideoEmbedder

logger = get_logger(__name__)

# Redis manager instance
redis_manager = RedisManager()
# VideoEmbedder instance for embedding (can be reused for books)
embedder = VideoEmbedder()

def process_book_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Process a CSV file containing book data.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        List[Dict]: List of processed book records
    """
    try:
        df = pd.read_csv(file_path)
        books = [dict(book) for book in df.to_dict(orient='records')]
        logger.info(f"Processed {len(books)} books from CSV.")
        return books
    except Exception as e:
        logger.error(f"Error processing book CSV: {e}")
        return []

def save_books_to_redis(books: List[Dict[str, Any]]) -> List[str]:
    """
    Save books to Redis with embeddings.

    Args:
        books (List[Dict]): List of book records to save

    Returns:
        List[str]: List of Redis keys for saved books
    """
    keys: List[str] = []
    for book in books:
        # Generate embedding for the book using VideoEmbedder (can be refactored for books)
        text = f"{book.get('book_title', '')} {book.get('author', '')}"
        try:
            book['embedding'] = embedder.get_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding for book: {e}")
            book['embedding'] = None

        # Save to Redis
        try:
            # Use a key format: book:<title>:<author>
            title = book.get('book_title', '').replace(' ', '_')
            author = book.get('author', '').replace(' ', '_')
            redis_key = f"book:{title}:{author}"
            redis_manager.set_json(redis_key, book)
            keys.append(redis_key)
            logger.info(f"Saved book to Redis: {redis_key}")
        except Exception as e:
            logger.error(f"Error saving book to Redis: {e}")
    logger.info(f"Saved {len(keys)} books to Redis.")
    return keys