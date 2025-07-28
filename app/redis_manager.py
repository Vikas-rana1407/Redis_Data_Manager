import redis
import logging
import json
from redis.commands.search.query import Query
from app.config import get_redis_config

logger = logging.getLogger(__name__)

class RedisManager:
    """
    Handles Redis connection and operations for storing and retrieving JSON data.
    """
    def __init__(self):
        config = get_redis_config()
        self.client = redis.Redis(
            host=config['host'],
            port=config['port'],
            password=config['password'],
            db=config['db'],
            decode_responses=True
        )
        logger.info('Connected to Redis')

    def set_json(self, key, value):
        """Set a JSON value in Redis under the given key."""
        self.client.set(key, json.dumps(value))
        logger.info(f'Set key {key} in Redis')

    def exists(self, key):
        """Check if a key exists in Redis."""
        return self.client.exists(key)

    def get_json(self, key):
        """Get a JSON value from Redis by key."""
        val = self.client.get(key)
        if isinstance(val, (bytes, str)):
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            return json.loads(val)
        return None

    def search(self, index: str, query: str, limit: int = 5):
        """
        Search the Redis index using RediSearch. Returns list of matching keys and their data.
        
        Args:
            index (str): Redis index name (e.g., 'book_idx' or 'video_idx')
            query (str): Full-text search query
            limit (int): Max number of results

        Returns:
            List[Dict]: List of dicts with 'id' and 'content'
        """
        try:
            search_obj = self.client.ft(index)
            redis_query = Query(query).paging(0, limit)
            results = search_obj.search(redis_query)

            return [
                {"id": doc.id, "content": self.get_json(doc.id)}
                for doc in results.docs
                if self.get_json(doc.id)
            ]
        except Exception as e:
            logger.error(f"🔍 Redis search failed on index {index}: {e}")
            return []
