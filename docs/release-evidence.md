# Release Evidence

Factual record of the final-project release checks for Task Tracker. All results below
were produced by actually running the commands shown, on Windows 10 with the project
venv (Python 3.11.9).

## Baseline

- **Branch:** `final-project`
- **Date:** 2026-08-12
- **Local app run command:** `uvicorn app.main:app --reload --port 8000`
- **/health result:** HTTP **200** —
  `{"status":"ok","timestamp":"2026-08-12T23:28:15.827117+00:00"}`
- **Frontend check:** served with `python -m http.server 5500 --directory frontend` and opened
  `http://localhost:5500/`. The Kanban board renders with all three columns (To Do / In Progress /
  Done); the `+ New Task` modal opens with Title, Description, Status, Priority, Assignee, Due date
  and Tags fields plus Save/Cancel; a task created through the API rendered on the board as a card
  with its description, tag chip, priority, assignee and Edit button — confirming the
  create/edit flow and the frontend-to-backend wiring still work.
- **Test command:** `python -m pytest tests/ -v`
- **Test result:** **45 passed**, 4 warnings, no failures. The warnings are pre-existing
  deprecation notices (`StarletteDeprecationWarning`) from the installed FastAPI/Starlette
  version and from `HTTP_422_UNPROCESSABLE_ENTITY`; they are not test failures and were not
  introduced by final-project work.

## CI evidence

- **Workflow file:** `.github/workflows/ci.yml` (triggers: `push` and `pull_request`)
- **Latest run link or note:**
  <https://github.com/maha-chal/task-tracker/actions/runs/31645766473> — **Success** (green),
  commit `c381934` on branch `final-project`, job `test` passed in 15s.
- **Test command used by CI:** `python -m pytest tests/ -v`
- **Shortcut check:**
  - no `continue-on-error` — confirmed absent from `ci.yml`
  - no `|| true` — confirmed absent from `ci.yml`
  - pytest is **not** skipped — the workflow runs the whole `tests/` directory
  - Python version is pinned to `"3.11"` (not vague or floating)
  - dependencies are installed explicitly via `pip install -r requirements.txt`

**Change made during the final project:** CI previously ran only
`python -m pytest tests/test_tasks.py -v` — a single file rather than the suite, which matches
the brief's "skipped pytest command" shortcut warning. Before changing it I verified that
`python -m pytest tests/ -v` collects **exactly the same 45 tests** (the legacy
`tests/verify_a.py` is not collected, because its filename does not match pytest's `test_*.py`
pattern). The command was therefore widened to `tests/` with no change in result and no risk.

## Docker evidence

- **Build command:** `docker build -t task-tracker .` — succeeded; image `task-tracker:latest`,
  258MB.
- **Run command (documented for users):** `docker run --rm -p 8000:8000 task-tracker`
  Verification was performed with the same command in detached form,
  `docker run -d -p 8000:8000 --name tt-check task-tracker`, so the health check could run in the
  same session. Container status: `Up`, `0.0.0.0:8000->8000/tcp`.
- **/health check:** HTTP **200** —
  `{"status":"ok","timestamp":"2026-08-12T23:19:26.480307+00:00"}`
- **Non-root user:** implemented and verified. `docker exec tt-check whoami` → `app`;
  `docker inspect --format "{{.Config.User}}" tt-check` → `app`.
- **No-baked-secrets check:**
  - `docker exec tt-check ls -la /app` → contains only the `app/` directory; `tests/` and
    `frontend/` are not copied into the image.
  - A search for env files inside the container (`find / -maxdepth 4 -name '*.env' -o -name
    '.env*'`) returned **no results** — no `.env`, credentials, or tokens are baked in.
  - Runtime command is explicit: `[uvicorn app.main:app --host 0.0.0.0 --port 8000]`.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README: "Expected result: **45 passed**" | Ran `python -m pytest tests/ -v` in the project venv | **True** — 45 passed, 4 warnings | None |
| README: the documented test command "is ... the one CI runs" | Compared `README.md` §5/§7 against `.github/workflows/ci.yml` after widening CI to `tests/` | **False** — README still named `tests/test_tasks.py` while CI ran `tests/` | Updated both README references (§5 and §7) to `python -m pytest tests/ -v` so docs and CI match |
| README §6: the Docker image "runs the **API only** ... as a non-root user on port 8000" | `docker exec tt-check whoami`; `docker inspect .Config.User`; `ls -la /app` inside the container | **True** — user is `app`, and only `app/` is present (no `tests/`, no `frontend/`) | None |
| README §4: `GET /health` returns `{"status": "ok", "timestamp": ...}` | `Invoke-WebRequest` against the local server **and** against the running container | **True** — HTTP 200 with that exact JSON shape in both cases | None |

Coverage note: these four checks span a **command** (pytest), **CI behavior** (workflow test
scope), **Docker behavior** (non-root, image contents), and an **endpoint/status code**
(`/health` → 200), satisfying the requirement that at least one checked claim involve a
command, endpoint, schema/status code, Docker behavior, or CI behavior.
