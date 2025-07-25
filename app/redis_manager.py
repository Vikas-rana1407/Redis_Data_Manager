#app/redis_manager.py
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

    def set_json(self, key, value):
        """Set a JSON value in Redis under the given key."""
        # Store as stringified JSON
        import json
        self.client.set(key, json.dumps(value))
        logger.info(f'Set key {key} in Redis')

    def exists(self, key):
        """Check if a key exists in Redis."""
        return self.client.exists(key)

    def get_json(self, key):
        """Get a JSON value from Redis by key."""
        import json
        val = self.client.get(key)
        if isinstance(val, (bytes, str)):
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            return json.loads(val)
        return None
