import redis
import logging
from app.utils.config import get_redis_config

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

    def get_client(self):
        """Return the raw Redis client."""
        return self.client
redis_client = RedisManager().get_client()
