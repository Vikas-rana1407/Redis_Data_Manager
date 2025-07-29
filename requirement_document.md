# Requirement Document: Redis Data Manager

## Purpose
A Python application to manage, process, and search YouTube video and book data in Redis. Supports transcript extraction, LLM tagging, embeddings, and search via a Gradio-based web UI. All actions and errors are logged to `app.log` for traceability.

## Modules
- **Video Processing**: Add YouTube videos by URL, extract transcript, tag with LLM, store in Redis. (See `app/videos/processor.py`)
- **Embedding**: Generate embeddings for searchable text, batch process transcripts, store enhanced data in Redis. (See `app/videos/embedder.py`)
- **Search**: Search videos by URL or title (full-text scan and semantic), delete by key. Book search by name. (See `app/utils/common.py`)
- **UI**: Web UI for add/search/delete via Gradio. (See `app/ui/`)
- **Config/Logger/Redis**: Centralized configuration, logging, and Redis operations. (See `app/config.py`, `app/utils/logger.py`, `app/redis_manager.py`)

## Workflow
1. User logs in via the web UI (Gradio-based authentication).
2. User enters a YouTube link in the UI.
3. App fetches transcript, tags with LLM, saves to Redis.
4. User can search videos by URL or title (full-text and semantic search).
5. User can delete videos by Redis key.
6. User can upload books via CSV; app processes and saves books to Redis. Book search by name is available.

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

## Extensibility
- Extend book search and logic in `books/` modules.
- Extend UI for additional data types or workflows.

## Logging
- All modules use a centralized logger (`app/utils/logger.py`).
- All actions, errors, and important events are logged to `app.log`.

## Requirements
See `requirements.txt` for dependencies.

## Notes
- Uses DeepInfra for LLM and embeddings.
- Redis must be accessible and configured in `.env`.
