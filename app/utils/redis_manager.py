
# Third-party imports
import redis

# App imports
from app.utils.config import get_redis_config
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)


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
            decode_responses=True
        )
        logger.info('Connected to Redis')

    def get_client(self):
        """
        Return the raw Redis client.
        """
        return self.client

# Singleton Redis client for app-wide use
redis_client = RedisManager().get_client()
