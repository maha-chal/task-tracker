# Task Tracker

A Task Tracker application with a Python/FastAPI backend and a vanilla HTML/CSS/JavaScript
Kanban-board frontend (no framework, no build step). Tasks have a title, description, status
(`ToDo`/`InProgress`/`Done`), priority (`Low`/`Medium`/`High`), assignee, due date, and tags.

The backend exposes a REST API (`/tasks`) with full CRUD, status-transition business rules, and
filtering. The frontend renders tasks as a drag-and-drop Kanban board with a create/edit modal.

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

## Run the backend

```
uvicorn app.main:app --reload
```

The API starts at `http://127.0.0.1:8000`. Check it's up:
```
curl http://127.0.0.1:8000/health
```
Expected response:
```json
{"status": "ok", "timestamp": "2026-07-14T12:00:00+00:00"}
```

Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`

## Open the frontend

With the backend running, open `frontend/index.html` directly in a browser (`file://...`), or
serve it locally:
```
cd frontend
python -m http.server 5500
```
then open `http://localhost:5500/`. Both origins are already allowed by the backend's CORS
configuration.

## Run tests

```
python -m pytest tests/test_tasks.py -v
```

Use `python -m pytest` (not the bare `pytest` command) — this ensures the project root is on
`sys.path` so `app` can be imported; the bare `pytest` script does not add it automatically.
