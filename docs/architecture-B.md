# Task Tracker — Architecture (Strategy B)

## 1. What the app does
A **local, single-user** course project (AGENTS.md §1): a Python/FastAPI backend exposes a REST task API; a single-file vanilla HTML/CSS/JS frontend renders a drag-and-drop Kanban board. **Storage is in-memory only — no database, no authentication, no deployment**; data is lost when the server stops. Endpoints: `GET /health`, `POST /tasks`, `GET /tasks` (filters `status`/`priority`/`overdue`/`tag`), `GET`/`PATCH`/`DELETE /tasks/{id}`.

## 2. Data model
One entity, **Task** (AGENTS.md §3):
- `id` (uuid4 string), `title` (required, trimmed, ≤200), `description`, `status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`), `assignee`, `due_date` (`YYYY-MM-DD`), `tags` (trimmed, non-blank, de-duplicated case-insensitively), `created_at`/`updated_at` (UTC; `updated_at` refreshed on update).

## 3. Request flow — creating a task
1. `POST /tasks` with a JSON body, validated against `TaskCreate`: `extra="forbid"` (unknown field → **422**), title required/≤200, tag rules, `due_date` format (AGENTS.md §3).
2. **Creation bypasses the status-transition rule** — a task may be created directly in any status (AGENTS.md §3).
3. Server assigns a uuid4 `id` and UTC `created_at`/`updated_at`, stores it in the in-memory dict.
4. Returns **201** with the created task.
5. *(from inspecting `frontend/index.html`)* the modal builds the payload, POSTs, then re-fetches `/tasks` and re-renders the board.

## 4. Key files
- `app/main.py` — FastAPI app, routes, CORS.
- `app/models.py` — Pydantic v2 models + validators.
- `app/storage.py` — in-memory task store.
- `app/business_rules.py` — status-transition rule (invalid → 422).
- `frontend/index.html` — single-file Kanban board.
- `tests/test_tasks.py` + `tests/conftest.py` — pytest suite + fixtures.
- `.github/workflows/ci.yml` — CI (installs deps, runs pytest).
- `Dockerfile` — multi-stage, API-only, non-root.
- `README.md` / `AGENTS.md` — human and agent docs.

## 5. Conventions
- **Validation:** Pydantic `extra="forbid"` → 422; title trimmed/≤200; tags trimmed, non-blank, de-duped case-insensitively; `due_date` must be `YYYY-MM-DD` (AGENTS.md §3).
- **Storage:** in-memory dict; uuid4 ids; UTC timestamps (AGENTS.md §3).
- **Business rule:** transitions `ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`; anything else (incl. same-status and `Done→ToDo`) → **422**, enforced on `PATCH` (AGENTS.md §3).
- **Error handling:** missing task → **404** on GET/PATCH/DELETE (AGENTS.md §3).
- **Overdue / filtering:** overdue = `due_date` set, before today's local date, status ≠ `Done`; `GET /tasks` filters combine with AND, tag match case-insensitive (AGENTS.md §3).
- **Frontend/backend:** CORS origins `localhost:5500`, `127.0.0.1:5500`, `"null"`; methods GET/POST/PATCH/DELETE; header `Content-Type`. **Tags & commas:** the frontend splits tag input on commas, so a comma can't be in one tag *via the UI* — not backend-enforced (AGENTS.md §3).

## 6. Not visible / assumptions
- No auth, database, or deployment — intentional (AGENTS.md §1, §5).
- `python-dotenv` is installed but **not wired up** — the app reads no `.env` (AGENTS.md §2).
- The create-flow frontend steps (step 5) and the `response_model` re-validation behavior come from **inspecting** `frontend/index.html` and `app/main.py`, not from AGENTS.md.
- One-page limit → route- and frontend-level detail is summarized.

---

*Context basis:* built from the actual `AGENTS.md` plus file summaries derived
from AGENTS.md's file references and `README.md` §8 (the Strategy-B context
placeholders were empty). Nothing here is invented; details beyond the structured
context are attributed to files explicitly inspected.
