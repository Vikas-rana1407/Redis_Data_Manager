
# app/videos/utils.py
# Utility functions for video processing, LLM calls, and YouTube metadata.

# Standard library imports
import os
import json
import re
from typing import Optional

# Third-party imports
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from app.utils.keyvault_loader import DEEPINFRA_TOKEN

# App imports
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

LLM_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

def ensure_dirs(dirs):
    """
    Ensure all directories in the list exist.
    Args:
        dirs (list): List of directory paths
    """
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL.
    Args:
        url (str): YouTube video URL
    Returns:
        str or None: Video ID if found, else None
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_video_title(video_id: str):
    """
    Fetch the title of a YouTube video by ID.
    Args:
        video_id (str): YouTube video ID
    Returns:
        str: Video title or 'Unknown Title' if not found
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        return title.text.replace(" - YouTube", "").strip() if title else "Unknown Title"
    except Exception as e:
        logger.error(f"Title fetch failed: {e}")
        return "Unknown Title"

def call_llm(prompt: str):
    """
    Call the DeepInfra LLM with a prompt and return the response.
    Args:
        prompt (str): Prompt for the LLM
    Returns:
        str or None: LLM response content if successful, else None
    """
    try:
        openai = OpenAI(
            api_key=DEEPINFRA_TOKEN,
            base_url="https://api.deepinfra.com/v1/openai",
        )
        completion = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None

def extract_json_response(response: str):
    """
    Extract and parse JSON from LLM response string.
    Args:
        response (str): LLM response string
    Returns:
        dict or None: Parsed JSON if successful, else None
    """
    match = re.search(r"```json(.*?)```", response, re.DOTALL)
    json_str = match.group(1).strip() if match else response.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        return None

def stringify(val):
    """
    Convert a value to a string, joining lists with commas.
    Args:
        val (Any): Value to stringify
    Returns:
        str: Stringified value
    """
    return ", ".join(val) if isinstance(val, list) else str(val)
