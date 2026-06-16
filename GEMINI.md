# Coding Standards & Guidelines - Green Job Bridge

This document details the standards and architecture rules for developers and agents working on the **Green Job Bridge** application.

## 1. Project Organization
- Keep everything clean, modular, and well-commented.
- Streamlit application is primarily built in [app.py](file:///c:/Users/p/Desktop/anti projects/green bridge/app.py).
- Database initialization and pre-population should reside in [init_db.py](file:///c:/Users/p/Desktop/anti projects/green bridge/init_db.py).
- Keep tests in [test_matching.py](file:///c:/Users/p/Desktop/anti projects/green bridge/test_matching.py).

## 2. API Integration Standards
- **Model Usage**: Use `models/text-embedding-004` (768 dimensions) for embeddings. Use `gemini-1.5-flash` for the Skill Translation Report generation to ensure fast response times and low cost.
- **Error Handling**: Wrap all Gemini API calls in `try-except` blocks. Specifically catch:
  - `google.api_core.exceptions.ResourceExhausted` (Rate limit / 429) -> Show a graceful user-facing retry message.
  - General network exceptions -> Show an offline/connection error message with a retry option.
- **API Key Management**: Never hardcode API keys. Load keys via `os.environ` or Streamlit Secrets. Fall back to loading from a `.env` file for local development.

## 3. Database & Matching Logic
- **Schema Integrity**: Always ensure required fields are fully filled. SQLite database should be stored at `green_jobs.db` by default (configurable via environment variable `DATABASE_PATH`).
- **Cosine Similarity**: Vector matching is calculated mathematically to avoid unnecessary external dependencies. Use `numpy` for operations or write a fast pure-python cosine similarity routine.
- **Database Connection**: Use Context Managers (`with sqlite3.connect(...) as conn:`) to prevent connection leaks.

## 4. UI/UX Design System
- **Theme**: A premium green/teal theme symbolizing sustainability and hope.
- **Loading State**: Provide a clear loading message or spinner during async operations (e.g., matching or generating the translation report).
- **Responsive Web Design**: Ensure elements stack neatly on mobile screens and utilize container-bound columns.
