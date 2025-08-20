"""
keyvault_loader.py
Loads the DeepInfra token from Azure Key Vault based on environment.
"""
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from app.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

# Load DeepInfra token at module import
def _load_deepinfra_token() -> str:
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME", f"{ENVIRONMENT}-zumlokeyvault")
    logger.info(f"Using Key Vault: {KEY_VAULT_NAME}")
    VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    secret = client.get_secret("deepinfra-api-key")
    logger.info("Loaded DeepInfra token from Key Vault (secret name: deepinfra-api-key).")
    if secret.value is None:
        raise ValueError("DEEPINFRA_TOKEN (deepinfra-api-key) secret not found in Key Vault.")
    return secret.value

DEEPINFRA_TOKEN = _load_deepinfra_token()
