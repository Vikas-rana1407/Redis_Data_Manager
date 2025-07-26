import logging
from app.redis_manager import RedisManager

logger = logging.getLogger(__name__)
redis_client = RedisManager()

def delete_multiple_keys(keys: str, expected_prefix: str) -> str:
    """
    Delete multiple Redis keys. Validates each key and returns status messages.

    Args:
        keys (str): Comma-separated Redis keys.
        expected_prefix (str): 'book:' or 'video:' to validate prefix.

    Returns:
        str: Multiline status messages for each key.
    """
    key_list = [key.strip() for key in keys.split(",") if key.strip()]
    if not key_list:
        return "⚠️ No keys provided."

    messages = []
    for key in key_list:
        if not key.startswith(expected_prefix):
            messages.append(f"❌ '{key}': Key must start with `{expected_prefix}`")
            continue

        if not redis_client.exists(key):
            messages.append(f"⚠️ '{key}': Key does not exist.")
            continue

        redis_client.client.delete(key)
        logger.info(f"✅ Deleted Redis key: {key}")
        messages.append(f"✅ '{key}': Successfully deleted.")

    return "\n".join(messages)
