"""
keyvault_loader.py
Loads the DeepInfra token from Azure Key Vault based on environment.
"""
import os
import threading
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from app.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

def _validate_env_vars():
    required_vars = ["ENVIRONMENT"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.critical(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    logger.info(f"ENVIRONMENT={os.getenv('ENVIRONMENT')}")

def _load_deepinfra_token(timeout_sec=10) -> str:
    _validate_env_vars()
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME", f"{ENVIRONMENT}-zumlokeyvault")
    logger.info(f"Using Key Vault: {KEY_VAULT_NAME}")
    VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    result = {}
    def fetch_secret():
        try:
            secret = client.get_secret("deepinfra-api-key")
            result['value'] = secret.value
        except Exception as e:
            result['error'] = e

    thread = threading.Thread(target=fetch_secret)
    thread.start()
    thread.join(timeout=timeout_sec)
    if thread.is_alive():
        logger.critical(f"Timeout: Could not fetch DeepInfra token from Key Vault in {timeout_sec} seconds.")
        raise TimeoutError(f"Timeout: Could not fetch DeepInfra token from Key Vault in {timeout_sec} seconds.")
    if 'error' in result:
        logger.critical(f"Error loading DeepInfra token from Key Vault: {result['error']}")
        raise result['error']
    if not result.get('value'):
        logger.critical("DEEPINFRA_TOKEN (deepinfra-api-key) secret not found in Key Vault.")
        raise ValueError("DEEPINFRA_TOKEN (deepinfra-api-key) secret not found in Key Vault.")
    logger.info("Loaded DeepInfra token from Key Vault (secret name: deepinfra-api-key).")
    return result['value']

DEEPINFRA_TOKEN = _load_deepinfra_token()
