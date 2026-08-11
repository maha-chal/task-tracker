# Task Tracker — Architecture (Strategy A)

## 1. What the app does
Task Tracker is a small, local, single-user web app for managing tasks on a Kanban board. A Python/FastAPI backend exposes a REST API for task CRUD, status-transition rules, and filtering; a single-file vanilla-JS frontend renders a drag-and-drop board with a create/edit modal, overdue highlighting, and tag filtering. Storage is in-memory only — data is lost when the server stops. No database, no authentication, no deployment.

## 2. Data model
One entity, **Task** (Pydantic models in `app/models.py`, split into `TaskCreate` / `TaskUpdate` / `TaskResponse`):
- `id` (UUID string, server-set), `title` (required, ≤200 chars), `description`, `status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`), `assignee`, `due_date` (`YYYY-MM-DD`), `tags` (list), `created_at`/`updated_at` (UTC, server-set).

## 3. Request flow — creating a task
1. Frontend modal submit builds a JSON payload and `POST`s to `/tasks`.
2. FastAPI validates the body against `TaskCreate` — unknown fields, blank/over-long title, bad tags, or malformed `due_date` return **422** automatically.
3. `storage.add_task` generates a UUID `id` and UTC `created_at`/`updated_at`, stores the task in the in-memory dict.
4. The response is validated against `TaskResponse` and returned as **201**.
5. Frontend closes the modal, re-fetches `/tasks`, and re-renders the board.

## 4. Key files
- `app/main.py` — FastAPI app, CORS, and the 6 routes (`/health` + task CRUD).
- `app/models.py` — Pydantic v2 models, field validators, status/priority enums.
- `app/storage.py` — in-memory dict store; UUID + UTC generation; CRUD helpers.
- `app/business_rules.py` — allowed status transitions (invalid → 422).
- `frontend/index.html` — single-file Kanban board (render, modal, drag-drop, fetch).
- `tests/test_tasks.py` — pytest API suite; `tests/conftest.py` — fixtures + storage reset.
- `.github/workflows/ci.yml` — CI: install deps, run pytest.
- `Dockerfile` — multi-stage, API-only image, non-root.
- `README.md` — run/test commands and project conventions.

## 5. Conventions
- **Validation:** Pydantic v2 with `extra="forbid"` (unknown field → 422); title trimmed & capped at 200; tags trimmed, non-blank, de-duplicated case-insensitively; `due_date` must be `YYYY-MM-DD`.
- **Storage:** module-level in-memory dict; ephemeral (lost on restart); no DB/ORM.
- **Error handling:** `HTTPException` 404 for missing tasks, 422 for validation and invalid status transitions; return values re-validated by `response_model`.
- **Frontend/backend:** REST + JSON over `fetch` to a hardcoded `http://localhost:8000`; CORS allows `localhost:5500`, `127.0.0.1:5500`, and `"null"`; all task data rendered via `textContent` (no HTML injection).

## 6. Not visible / assumptions
- No auth, database, or deployment — confirmed intentional in `README.md`/code, not an oversight.
- `python-dotenv` is a dependency but **not wired up**; the app reads no `.env`.
- No production/scaling/observability concerns exist in this repo (out of scope by design).
- The one-page limit means route-level and frontend detail is summarized, not exhaustive.
