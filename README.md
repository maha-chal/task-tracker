# Task Tracker API — Skeleton

A minimal FastAPI skeleton for the Module 1 Task Tracker project. This stage
only includes a health check endpoint — CRUD endpoints will be added in a
later step.

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy the example environment file:
   ```
   copy .env.example .env       # Windows
   cp .env.example .env         # macOS/Linux
   ```

## Run

```
uvicorn app.main:app --reload
```

The server starts at http://127.0.0.1:8000.

## Test the health endpoint

```
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-07-14T12:00:00+00:00"}
```

## Interactive docs

Open http://127.0.0.1:8000/docs in a browser to see the auto-generated
Swagger UI.
