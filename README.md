# Redis Data Manager

## Overview
A modular Python application for managing and searching YouTube video and book data in Redis. Supports transcript extraction, LLM tagging, embeddings, and full-text/semantic search.

## Features
- Add YouTube videos by URL (mobile/web)
- Extract transcript and tag with LLM
- Store processed and embedded data in Redis
- Search videos by URL or title
- Delete videos by Redis key
- Upload books via CSV, embed and save to Redis, search books by name

## Structure
- `app/` - Main application code
  - `videos/processor.py` - Add/process YouTube videos
  - `videos/embedder.py` - Embedding and batch processing
  - `utils/common.py` - Search and deletion logic
  - `ui/ui.py` - CLI UI logic
  - `redis_manager.py` - Redis connection/operations
  - `logger.py` - Logging setup
  - `config.py` - Configuration loading

## Requirements
See `requirements.txt` for dependencies.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up `.env` with Redis and DeepInfra credentials.
3. Run the app:
   ```bash
   python -m app.app
   ```
4. Use the CLI to add/search/delete YouTube videos.

## Search
- Videos: Search by URL or title (full-text scan)
- Books: Search by name

## Extending
- Extend book search and logic in `books/` modules.
- UI can be extended for web or desktop.

## License
MIT