
# Standard library imports
import os

# Third-party imports
from typing import Dict, Any
from dotenv import load_dotenv

# App imports
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def get_redis_config() -> Dict[str, Any]:
    """
    Get Redis connection configuration from environment variables. Fail fast if missing.
    Returns:
        Dict[str, Any]: Redis connection parameters
    """
    required_vars = ['REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD']
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.critical(f"Missing required Redis environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required Redis environment variables: {', '.join(missing)}")
    redis_port = os.getenv('REDIS_PORT')
    if redis_port is None:
        logger.critical("REDIS_PORT environment variable is missing or empty.")
        raise RuntimeError("REDIS_PORT environment variable is missing or empty.")
    config = {
        'host': os.getenv('REDIS_HOST'),
        'port': int(redis_port),
        'password': os.getenv('REDIS_PASSWORD')
    }
    logger.info(f"Loaded Redis config: host={config['host']}, port={config['port']}")
    return config

