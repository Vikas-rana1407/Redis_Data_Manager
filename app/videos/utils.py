# app/videos/utils.py

import os
import json
import re
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
DEEPINFRA_TOKEN = os.getenv("DEEPINFRA_TOKEN")
LLM_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

def ensure_dirs(dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_video_title(video_id: str):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        return title.text.replace(" - YouTube", "").strip() if title else "Unknown Title"
    except Exception as e:
        print(f"❌ Title fetch failed: {e}")
        return "Unknown Title"

def call_llm(prompt: str):
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

def extract_json_response(response: str):
    match = re.search(r"```json(.*?)```", response, re.DOTALL)
    json_str = match.group(1).strip() if match else response.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        return None

def stringify(val):
    return ", ".join(val) if isinstance(val, list) else str(val)
