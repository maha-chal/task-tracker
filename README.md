# Task Tracker — Module 4

A small Task Tracker with a **Python / FastAPI** backend and a **vanilla HTML/CSS/JavaScript**
Kanban-board frontend (no framework, no build step). Built for the AUB AI-Assisted Coding course;
storage is in-memory only.

Tasks have a title, description, status (`ToDo` / `InProgress` / `Done`), priority
(`Low` / `Medium` / `High`), assignee, due date, and tags. The backend exposes a REST API under
`/tasks` with full CRUD, status-transition rules, and filtering. The frontend renders tasks as a
drag-and-drop Kanban board with a create/edit modal, overdue highlighting, and tag filtering.

> Scope note: this is a local, single-user course project. There is **no database, no
> authentication, and no deployment** — task data lives in memory and is lost when the server
> stops.

## 1. Project overview

- **Backend:** FastAPI app (`app/main.py`) with Pydantic v2 models, an in-memory store, and a
  status-transition rule.
- **Frontend:** single-file Kanban board (`frontend/index.html`) — three columns
  (To Do / In Progress / Done), drag a card to change status, create/edit modal, overdue cards
  flagged with a red border + "Show overdue only" filter, tag chips + "Filter by tag" field.
- **API endpoints:** `GET /health`, `POST /tasks`, `GET /tasks` (filter by `status`, `priority`,
  `overdue`, `tag`), `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`.
- **Interactive docs:** Swagger UI at `http://127.0.0.1:8000/docs` when the app is running.

## 2. Prerequisites

- **Python 3.11** (the course venv uses 3.11.9; the Docker image and CI use `3.11`).
- **pip** and the ability to create a virtual environment (`venv`).
- **Docker** — only if you want to run the containerized version (section 6).
- A modern web browser for the frontend.

## 3. Local setup

Run all commands from the repository root.

Create a virtual environment:

```bash
python -m venv venv
```

> **Check your Python version first.** This project requires **Python 3.11** — a venv built on a
> different version (e.g. 3.14) will install mismatched binary wheels and fail to import at
> runtime. Confirm with `python --version`. If your default `python` is **not** 3.11, create the
> venv with the launcher instead so it's pinned to the right interpreter:
>
> ```bash
> py -3.11 -m venv venv
> ```

Activate it — **Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

**Windows (cmd):**

```bash
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

> Note: `.env.example` (`PORT`, `APP_ENV`) exists, but the app does **not** read it —
> `python-dotenv` is installed but not wired up, and the port comes from the `--port` flag below.
> Copying it to `.env` is optional and has no effect on runtime.

## 4. Run the app locally

Start the backend (course command):

```bash
uvicorn app.main:app --reload --port 8000
```

The API serves at `http://127.0.0.1:8000`. Uvicorn takes over the terminal while it runs, so open
a **second** terminal to test it:

```bash
curl http://127.0.0.1:8000/health
```

Expected response (timestamp will differ):

```json
{"status": "ok", "timestamp": "2026-08-02T12:00:00+00:00"}
```

Open the frontend — serve it from the repo root (the backend's CORS already allows
`localhost:5500`):

```bash
python -m http.server 5500 --directory frontend
```

Then open `http://localhost:5500/`. You can alternatively open `frontend/index.html` directly as a
`file://` page — the CORS config also allows the `"null"` origin that produces.

## 5. Run tests

Use the module form — it puts the project root on `sys.path` so `app` can be imported. This is the
confirmed-working command and the one CI runs:

```bash
python -m pytest tests/test_tasks.py -v
```

Expected result: **45 passed**.

> Note: bare `pytest -v` does **not** work in this repo — it fails with
> `ModuleNotFoundError: No module named 'app'`, because there is no `pytest.ini` / `pyproject.toml`
> or `tests/__init__.py` to add the project root to `sys.path`. Always use the `python -m pytest`
> form above.

## 6. Run with Docker

The repo includes a multi-stage `Dockerfile` that runs the **API only** (it copies `app/` into the
image — not `frontend/` or `tests/`) as a non-root user on port 8000.

Build the image:

```bash
docker build -t task-tracker .
```

Run the container:

```bash
docker run --rm -p 8000:8000 task-tracker
```

The API is then available at `http://127.0.0.1:8000` (including `/docs`). To use the frontend
against it, serve `frontend/` separately as in section 4.

> Notes: task data is in-memory and is discarded when the container stops. The container runs the
> API only — it does not serve the Kanban HTML. This is for **local/containerized runs, not
> deployment or production**.

## 7. CI workflow summary

GitHub Actions workflow: `.github/workflows/ci.yml`.

- **Triggers:** every `push` and every `pull_request`.
- **Runner:** `ubuntu-latest`, Python `3.11`.
- **Steps:** checkout → set up Python → `pip install -r requirements.txt` → run
  `python -m pytest tests/test_tasks.py -v`.
- **Scope:** tests only. No build, publish, or deployment steps.

## 8. Project structure

```text
task-tracker/
├─ app/
│  ├─ __init__.py
│  ├─ main.py            # FastAPI app + routes
│  ├─ models.py          # Pydantic v2 models + validators
│  ├─ storage.py         # in-memory task store
│  └─ business_rules.py  # status-transition rule (422 on invalid)
├─ frontend/
│  └─ index.html         # single-file Kanban board (no build step)
├─ tests/
│  ├─ test_tasks.py      # pytest suite (run by the test command + CI)
│  ├─ conftest.py        # fixtures
│  └─ verify_a.py        # legacy manual script — NOT part of the pytest suite
├─ docs/
│  ├─ midcourse/         # user-stories, mini-adr, prompt-log, reflection, verification
│  └─ module4/           # verification.md
├─ .github/workflows/
│  └─ ci.yml             # GitHub Actions test workflow
├─ Dockerfile            # multi-stage image, API only, non-root, port 8000
├─ .dockerignore
├─ requirements.txt
├─ .env.example          # PORT/APP_ENV — present but NOT read by the app
├─ CLAUDE.md             # project instructions for Claude Code
└─ README.md
```

## 9. Project conventions and current limitations

- **In-memory storage:** all tasks are lost on server (or container) restart. No database.
- **No authentication or authorization.** Every request is unauthenticated.
- **Not deployed / not production-ready** — intended for local course use.
- **Status transitions** (`app/business_rules.py`): allowed are `ToDo → InProgress`,
  `InProgress → Done`, `Done → InProgress`. Any other change — including same-status
  (e.g. `ToDo → ToDo`) and `Done → ToDo` — returns HTTP **422** with the allowed list.
- **Validation:** unknown fields are rejected (`extra="forbid"` → 422); title is required,
  trimmed, and capped at 200 chars; tags are trimmed, non-blank, and de-duplicated
  case-insensitively; malformed `due_date` returns 422.
- **Overdue logic:** a task is overdue when its `due_date` is before the **server's local date**
  (`date.today()`) and its status is not `Done`.
- **Tags:** cannot contain a comma (the frontend uses comma as the input delimiter).
- **CORS** (`app/main.py`): origins `http://localhost:5500`, `http://127.0.0.1:5500`, and
  `"null"`; methods `GET, POST, PATCH, DELETE`; header `Content-Type`.
- **`.env` handling:** `python-dotenv` is a dependency but unused; the app reads no environment
  file.

## 10. Technical notes / decisions

- **Architecture decision record:** [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) —
  why the project extended in-memory storage instead of introducing SQLite, plus the accepted
  trade-offs and known limitations.
- **Module 4 verification log:** [`docs/module4/verification.md`](docs/module4/verification.md) —
  direct verification of API claims (status-transition rule, 422 validation behaviors) against the
  running backend.
