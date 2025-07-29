
# Standard library imports
import os
# Third-party imports
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_redis_config() -> Dict[str, Any]:
    """
    Get Redis connection configuration from environment variables.
    Returns:
        Dict[str, Any]: Redis connection parameters
    """
    return {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'password': os.getenv('REDIS_PASSWORD', None),
        'db': int(os.getenv('REDIS_DB', 0)),
    }

def get_credentials() -> tuple[str, str]:
    """
    Get application credentials from environment variables.
    Returns:
        tuple[str, str]: (username, password)
    """
    return os.getenv('APP_USERNAME', ''), os.getenv('APP_PASSWORD', '')

def get_deepinfra_key() -> str:
    """
    Get DeepInfra API key from environment variables.
    Returns:
        str: DeepInfra API key
    """
    return os.getenv('DEEPINFRA_API_KEY', '')