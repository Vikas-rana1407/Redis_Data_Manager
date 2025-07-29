# Redis Data Manager

## Overview
A Python application for managing and searching YouTube video and book data in Redis. Features transcript extraction, LLM tagging, embeddings, and full-text/semantic search via a Gradio web UI. All actions and errors are logged to `app.log` for traceability.

## Features
- Add YouTube videos by URL (mobile/web)
- Extract transcript and tag with LLM
- Store processed and embedded data in Redis
- Search videos by URL or title (full-text and semantic)
- Delete videos by Redis key
- Upload books via CSV, embed and save to Redis, search books by name
- Web UI for all operations (Gradio-based authentication and interface)
- Centralized logging to `app.log` for all modules

## File Structure
```
app.log
main.py
requirements.txt
requirement_document.md
README.md
app/
  utils/
    common.py
    config.py
    redis_manager.py
    logger.py
  ui/
    ui.py
    auth.py
    header.py
    add_data.py
    search_data.py
    delete_data.py
  videos/
    processor.py
    embedder.py
    new_tags.py
    prompt.py
  books/
    processor.py
  data/
    transcripts/
    processed_transcripts/
    formatted_jsons/
```

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up `.env` with Redis and DeepInfra credentials.
3. Run the app:
   ```bash
   python main.py
   ```
4. Use the web UI to add/search/delete YouTube videos and books.

## Logging
- All modules use a centralized logger (`app/utils/logger.py`).
- All actions, errors, and important events are logged to `app.log`.

## Search
- Videos: Search by URL or title (full-text and semantic)
- Books: Search by name

## Extending
- Extend book search and logic in `books/` modules.
- Extend UI for additional data types or workflows.

## Requirements
See `requirements.txt` for dependencies.

## License
MIT