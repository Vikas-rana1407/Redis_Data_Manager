
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
        try:
            self.client = redis.Redis(
                host=config['host'],
                port=config['port'],
                password=config['password'],
                decode_responses=True,
                socket_connect_timeout=5,  # seconds
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info('Connected to Redis')
        except Exception as e:
            logger.critical(f'Failed to connect to Redis: {e}')
            raise RuntimeError(f'Failed to connect to Redis: {e}')

    def get_client(self):
        """
        Return the raw Redis client.
        """
        return self.client

# Singleton Redis client for app-wide use
redis_client = RedisManager().get_client()
