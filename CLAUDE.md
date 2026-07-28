# CLAUDE.md

Project instructions for Claude Code working in this repository.

## What this project is

A Task Tracker REST API (Python/FastAPI) with a vanilla HTML/CSS/JavaScript Kanban-board
frontend — no framework, no build step. Built incrementally across an AUB AI-Assisted Coding
course: Modules 1-3 (CRUD, business rules, Kanban UI with drag-and-drop) and a mid-course project
adding due dates/overdue filter and tags/tag filter. See `README.md` for setup/run instructions,
`CONTEXT.md` for architecture decisions and requirements history, and `docs/midcourse/` for the
mid-course project's user stories, mini-ADR, prompt log, verification evidence, and reflection.

## Running things

- Backend: `uvicorn app.main:app --reload` (starts at `http://127.0.0.1:8000`; docs at `/docs`).
- Frontend: open `frontend/index.html` directly (`file://`), or serve it via
  `python -m http.server 5500` from inside `frontend/`.
- Tests: `python -m pytest tests/test_tasks.py -v` — **use `python -m pytest`, not bare
  `pytest`**. The bare `pytest` command does not add the project root to `sys.path`, so `app`
  fails to import.

## Architecture conventions

- **Storage:** in-memory only (a `dict` in `app/storage.py`) — no database. This is a deliberate,
  documented decision (see `CONTEXT.md` ADR-001 and `docs/midcourse/mini-adr.md`), not an
  oversight. Data is lost on every restart; that's expected.
- **Models:** Pydantic v2 syntax only — `field_validator` (not `@validator`), `ConfigDict` (not
  `class Config`), `model_dump()`/`model_copy()` (not `.dict()`). All request/response models use
  `model_config = ConfigDict(extra="forbid")`.
- **Status transitions:** restricted to the pairs in `VALID_TRANSITIONS` in
  `app/business_rules.py`. Don't assume a transition is valid or invalid without checking that set
  — it does not simply block all backward moves (e.g. `Done → InProgress` is allowed; `Done →
  ToDo` is not).
- **Partial updates:** `TaskUpdate` fields are all optional; omitting a field leaves it unchanged,
  sending an explicit `null`/`[]` clears it. This pattern is already established for `assignee`,
  `due_date`, and `tags` — keep it consistent for any new optional field.

## Working style expectations

- **Scope discipline:** do exactly what's asked in each request. Don't add authentication, a
  database, Docker/deployment, new frameworks, or unrelated features unless explicitly requested,
  even if they seem like natural next steps. This project is built module-by-module for course
  deliverables, and unrequested scope creep makes it harder to track what belongs to which module.
- **Small steps:** when implementing a feature, work one file/concern at a time (models → storage
  → routes → tests → frontend), verifying each layer before moving to the next, rather than
  generating a large multi-file change at once.
- **Verify, don't assume:** before asserting that existing code "already handles" a new case
  correctly, check it directly (a quick script, a manual test) rather than reasoning from pattern
  similarity alone. This project has already been bitten once by an unverified assumption
  (Pydantic's `date` type silently accepting a Unix timestamp instead of rejecting malformed
  input) — verify claims before they go into a prompt, a test, or documentation.
- **Git:** never push to the remote (`origin`, `mid-course-project` branch) without explicit
  confirmation in chat, even if a local commit was just made. The mid-course project has already
  been submitted; treat further pushes as sensitive until told otherwise.
