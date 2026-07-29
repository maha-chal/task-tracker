# CLAUDE.md

Project instructions for Claude Code working in this repository (Module 4 Task Tracker).

## 1. Tech stack

- Python 3.11.9 (confirmed via `venv\Scripts\python.exe --version`; not pinned in
  `requirements.txt` itself, so re-verify if the venv is ever recreated)
- FastAPI (`fastapi>=0.110`)
- Pydantic v2 (`pydantic>=2.6`)
- Uvicorn (`uvicorn[standard]>=0.29`)
- pytest (`pytest>=9.0`)
- httpx (`httpx>=0.28`)
- python-dotenv (`python-dotenv>=1.0`)
- Frontend: vanilla JavaScript (`frontend/index.html`, referenced in `README.md`) — no framework,
  no build step

## 2. Exact run command used in this course

```
uvicorn app.main:app --reload --port 8000
```

## 3. Exact test command used in this course

```
pytest -v
```
Note: bare `pytest` has been observed to fail in this repo with `ModuleNotFoundError: No module
named 'app'`, because it doesn't add the project root to `sys.path`. If that happens, use
`python -m pytest tests/test_tasks.py -v` instead, which has been confirmed to work.

## 4. Architecture summary

- Backend: `app/main.py` (FastAPI app + routes), `app/models.py` (Pydantic models),
  `app/storage.py` (in-memory store), `app/business_rules.py` (status-transition rule).
- Frontend: `frontend/index.html` (single-file Kanban board).
- Tests: `tests/test_tasks.py`, `tests/conftest.py`. `tests/verify_a.py` also exists (a legacy
  manual verification script, not part of the pytest suite run by the test command above).
- Task rules (status-transition validation) live in `app/business_rules.py`.

## 5. Business rules (verified from `app/business_rules.py` and `app/models.py`)

- `TaskStatus` values: `ToDo`, `InProgress`, `Done`.
- `VALID_TRANSITIONS`: `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress`.
- Any other transition (including same-status, e.g. `ToDo → ToDo`, and `Done → ToDo`) raises
  `HTTPException(422)` listing the allowed transitions.

## 6. UI states and CORS notes

- CORS (`app/main.py`): `allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "null"]`,
  `allow_methods=["GET", "POST", "PATCH", "DELETE"]`, `allow_headers=["Content-Type"]`.
- UI behaviors per `README.md`'s Features section: three-column Kanban board, drag-and-drop status
  updates, create/edit modal, overdue tasks highlighted with a red border, "Show overdue only"
  filter, tag chips on cards, "Filter by tag" field.
- `[VERIFY]` — no explicit "loading / empty / error / ready" state documentation found in the
  files read for this revision.

## 7. Do-not rules

- Do not add authentication, a database, deployment steps (Docker, cloud, etc.), or major UI
  changes without asking first.
- Do not change application code as part of documentation updates.
- Do not invent version numbers or business rules not present in the code — mark uncertain items
  `[VERIFY]` instead.
