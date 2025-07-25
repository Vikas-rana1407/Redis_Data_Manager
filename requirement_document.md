# Requirement Document: Redis Data Manager

## Purpose
A Python application to manage, process, and search YouTube video and book data in Redis. Supports transcript extraction, LLM tagging, embeddings, and search.

## Modules
- **Video Processing**: Add YouTube videos by URL, extract transcript, tag with LLM, store in Redis.
- **Embedding**: Generate embeddings for searchable text, batch process transcripts, store enhanced data in Redis.
-- **Search**: Search videos by URL or title (full-text scan), delete by key. Book search by name (implemented).
- **UI**: CLI for add/search/delete. Web UI can be added later.
- **Config/Logger/Redis**: Centralized configuration, logging, and Redis operations.

## Workflow
1. User enters YouTube link (mobile/web) in UI.
2. App fetches transcript, tags with LLM, saves to Redis.
3. User can search videos by URL or title.
4. User can delete videos by Redis key.
5. (Books: User uploads CSV, app processes and saves books to Redis. Search by name is implemented.)

## Extensibility
- Extend book search logic in `books/` modules.
- Extend UI for web/desktop.

## Requirements
See `requirements.txt` for dependencies.

## Notes
- Uses DeepInfra for LLM and embeddings.
- Redis must be accessible and configured in `.env`.
