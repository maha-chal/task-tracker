# Task Tracker — Architecture (Strategy C)

## 1. What the app does
Task Tracker is a **REST API for managing tasks**, built with FastAPI (app title "Task Tracker API"). It supports creating, listing (with `status`/`priority`/`overdue`/`tag` filters), retrieving, updating, and deleting tasks, with input validation and a status-transition check on update. Tasks are held in an in-memory dictionary. Any user-facing frontend/UI is **not visible from the files I read**.

## 2. Data model
One entity, **Task** (`app/models.py`), as `TaskCreate` / `TaskUpdate` / `TaskResponse`:
- `id` (string), `title` (required, trimmed, ≤200), `description` (default `""`), `status` (enum `ToDo`/`InProgress`/`Done`, default `ToDo`), `priority` (enum `Low`/`Medium`/`High`, default `Medium`), `assignee` (optional), `due_date` (optional; must be `YYYY-MM-DD`), `tags` (list; trimmed, non-blank, de-duplicated case-insensitively), `created_at`/`updated_at` (UTC, server-set in storage).

## 3. Request flow — creating a task
1. `POST /tasks` with a JSON body validated against `TaskCreate`: `extra="forbid"` (unknown fields → **422**), title required/≤200, tag rules, `due_date` must be `YYYY-MM-DD` (`app/main.py`, `app/models.py`).
2. `storage.add_task` assigns a uuid4 `id` and UTC `created_at`/`updated_at`, stores it in the in-memory dict, returns it.
3. The route responds **201** with the task.
4. No status-transition check runs on create — that check appears only on `PATCH`.
5. What a frontend does before/after this request is **not visible from the files I read**.

## 4. Key files
Only these are visible from the files I read (fewer than five; listing more would require inferring files I did not read):
- `app/main.py` — FastAPI app, CORS, routes (`/health` + task CRUD).
- `app/models.py` — Pydantic models + validators, status/priority enums.
- `app/storage.py` — in-memory dict store, uuid/UTC generation, CRUD helpers, overdue check.
- `app/business_rules.py` — imported by `main.py` for `validate_status_transition`; its contents are **not visible from the files I read**.
- Frontend, tests, CI, Docker, README: **not visible from the files I read**.

## 5. Conventions
- **Validation:** Pydantic `extra="forbid"` → 422 on unknown fields; title trimmed & ≤200; tags trimmed/non-blank/de-duped case-insensitively; `due_date` must be `YYYY-MM-DD` (`app/models.py`).
- **Storage:** module-level in-memory dict (`app/storage.py`); uuid4 string ids; UTC timestamps; `updated_at` refreshed on update; a `_reset()` clears the store. No database/persistence beyond the in-memory dict is visible.
- **Error handling:** missing task → **404** with detail `Task with id {id} not found` on GET/PATCH/DELETE; invalid status transition on `PATCH` → **422** (via `validate_status_transition`) — the *specific allowed transitions* are **not visible from the files I read**.
- **Frontend/backend interaction:** CORS allows origins `http://localhost:5500`, `http://127.0.0.1:5500`, `"null"`; methods GET/POST/PATCH/DELETE; header `Content-Type` (`app/main.py`) — implying a browser client on `:5500`, but the frontend itself is **not visible from the files I read**.
- **Authentication:** no auth is present in the files I read.

## 6. Not visible / assumptions
- The frontend/UI (existence, framework, behavior) — **not visible from the files I read**.
- The specific allowed status transitions (`business_rules.py`) — **not visible from the files I read**.
- Tests, CI, Docker, README, run/deploy instructions — **not visible from the files I read**.
- Whether storage persists beyond process memory — only an in-memory dict is present.
