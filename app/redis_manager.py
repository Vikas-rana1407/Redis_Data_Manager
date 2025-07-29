import redis
import logging
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

    
    def exists(self, key):
        """Check if a key exists in Redis."""
        return self.client.exists(key)

    def get_json(self, key):
        try:
            val = self.client.json().get(key)
            return val
        except Exception as e:
            logger.error(f"Error fetching JSON for key {key}: {e}")
            return {"error": f"Could not fetch data for key: {key}"}

    def get_all_keys(self, pattern="*") -> list:
        """Return all keys matching a given pattern."""
        return self.client.keys(pattern)

redis_client = RedisManager()
