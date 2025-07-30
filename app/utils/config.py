
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
    Get Redis connection configuration from environment variables.
    Returns:
        Dict[str, Any]: Redis connection parameters
    """
    config = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'password': os.getenv('REDIS_PASSWORD', None),
        'db': int(os.getenv('REDIS_DB', 0)),
    }
    logger.info(f"Loaded Redis config: {config}")
    return config

