# AGENTS.md — Task Tracker

Contract for AI coding agents working in this repository. Human setup/onboarding
lives in `README.md`; this file is the agent-facing guidance.

## 1. Project summary

Task Tracker is a small, **local, single-user** course project (AUB AI-Assisted
Coding). A Python/FastAPI backend exposes a REST task API; a single-file vanilla
HTML/CSS/JS frontend renders a drag-and-drop Kanban board. **Storage is in-memory
only — no database, no authentication, no deployment**; data is lost when the
server stops. *(README.md:1–14; app/main.py)*

Endpoints: `GET /health`, `POST /tasks`, `GET /tasks` (filters: `status`,
`priority`, `overdue`, `tag`), `GET /tasks/{id}`, `PATCH /tasks/{id}`,
`DELETE /tasks/{id}`. *(app/main.py:28–198)*

## 2. Tech stack & supported commands

Stack *(requirements.txt)*: Python 3.11 *(README.md:29; CLAUDE.md notes venv
3.11.9)*, FastAPI `>=0.110`, Pydantic v2 `>=2.6`, Uvicorn[standard] `>=0.29`,
pytest `>=9.0`, httpx `>=0.28`. `python-dotenv >=1.0` is installed but **not
wired up** — the app reads no `.env`. *(README.md:77–79, 207)* No
`pyproject.toml`/`pytest.ini` exists.

Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

*(README.md:86)*

Serve the frontend:

```bash
python -m http.server 5500 --directory frontend
```

*(README.md:106)*

Run tests (only supported form — puts the project root on `sys.path`):

```bash
python -m pytest tests/test_tasks.py -v
```

*(README.md:118; CI uses the same per README.md:158–159.)* Bare `pytest` **fails**
with `ModuleNotFoundError: No module named 'app'` *(README.md:123–126)*. README
states the expected result is **"45 passed"** *(README.md:121)* — not
independently re-run in this review.

Docker (API only, non-root, port 8000):

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```

*(README.md:136, 142)*

## 3. Business rules visible in code

- **Statuses:** `ToDo`, `InProgress`, `Done`. *(app/models.py:8–11)*
- **Priorities:** `Low`, `Medium`, `High`. *(app/models.py:14–17)*
- **Status transitions:** allowed = `ToDo→InProgress`, `InProgress→Done`,
  `Done→InProgress`. Any other pair — **including same-status** (e.g.
  `ToDo→ToDo`) and `Done→ToDo` — raises HTTP **422** with the allowed list.
  *(app/business_rules.py:5–9, 31–36; enforced on PATCH at app/main.py:166–170)*
- **Creation bypasses the transition rule:** a task may be created directly in
  any status. *(app/main.py:51–59)*
- **Validation** (Pydantic `extra="forbid"` → unknown fields 422)
  *(app/models.py:21, 64, 111)*:
  - `title`: required, trimmed, max 200 chars → else 422. *(app/models.py:31–39)*
  - `tags`: each trimmed, blank rejected, de-duplicated case-insensitively.
    *(app/models.py:48–60)*
  - `due_date`: must be a string in `YYYY-MM-DD` form; non-string → 422.
    *(app/models.py:41–46)*
- **Overdue:** a task is overdue when `due_date` is set, `due_date < today's
  local date`, and status ≠ `Done`. *(app/storage.py:39–55)*
- **Filtering** (`GET /tasks`): `status`, `priority`, `overdue`, `tag`; combined
  with **AND**; tag match case-insensitive.
  *(app/storage.py:58–90; app/main.py:82–109)*
- **IDs & timestamps:** `id` = uuid4 string; `created_at`/`updated_at` = UTC;
  `updated_at` refreshed on update. *(app/storage.py:22–35, 124)*
- **Missing task → 404** on GET/PATCH/DELETE.
  *(app/main.py:130–132, 168–174, 196–198)*
- **CORS:** origins `http://localhost:5500`, `http://127.0.0.1:5500`, `"null"`;
  methods `GET/POST/PATCH/DELETE`; header `Content-Type`. *(app/main.py:16–25)*
- **Tags & commas (frontend-only):** the frontend splits the tag input on
  commas, so a comma cannot be part of a single tag *via the UI*
  *(frontend/index.html:769–772, 435)*. This is **not** backend-enforced —
  `app/models.py:48–60` does not reject commas, so the API itself would accept a
  tag containing one.

## 4. Module 5 guardrails (agent working rules)

> **Scope — temporary, phase-specific.** These rules apply during the
> **Module 5 grading/governance phase**, when the focus is reviewing and
> governing existing work rather than building features. They are deliberately
> restrictive for that phase and should be revisited or lifted once Module 5 is
> complete. They are **not** the repository's permanent policy — the standing
> rules live in Section 5.

- **Docs-first:** prefer read-only analysis; write only under `docs/` unless a
  different path is explicitly approved.
- **No `app/` changes** during Module 5 unless the human asks for one specific,
  minimal fix.
- **One bounded task per thread** — do not bundle or pre-empt later steps.
- **Announce intent first:** state the task understood, files to inspect, and
  whether edit permission is needed.
- **Cite files** inspected when making claims about the repo.
- **Admit uncertainty:** if a file isn't visible or something is unclear, say so
  — do not guess.

## 5. Security & governance reminders

- **Never** paste, echo, commit, or expose secrets/credentials/tokens.
  `.env.example` holds only non-secret placeholders (`PORT`, `APP_ENV`) and is
  not read by the app. *(README.md:77–79)*
- **No destructive commands** (data deletion, force-push, history rewrite, mass
  file removal) without explicit approval.
- **Cite evidence** (file + line range) for every claim about the code.
- **Do not invent** findings, commands, versions, or rules — mark anything
  unverifiable as "not confirmed."
- Storage is in-memory and single-user with **no auth layer** — do not assume
  access controls exist. *(README.md:193–195)*
