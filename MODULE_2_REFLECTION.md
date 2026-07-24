# Module 2 Reflection — Task Tracker API

## What I built

Starting from the Module 1 skeleton (a single `/health` endpoint), I added the
full CRUD layer for the Task Tracker API:

- **Data model** (`app/models.py`): `TaskStatus` and `TaskPriority` enums,
  and `TaskCreate` / `TaskUpdate` / `TaskResponse` Pydantic v2 models, with
  strict `extra="forbid"` validation and a shared title-validation rule
  (strip whitespace, reject blank, reject over 200 characters).
- **In-memory storage** (`app/storage.py`): a module-level dict acting as
  the data store, with `add_task`, `get_all_tasks`, `get_task_by_id`,
  `update_task`, `delete_task`, and a test-only `_reset`.
- **Routes** (`app/main.py`): `POST /tasks`, `GET /tasks` (with optional
  `status`/`priority` filters), `GET /tasks/{id}`, `PATCH /tasks/{id}`,
  `DELETE /tasks/{id}` — each added incrementally and verified before
  moving to the next.
- **Business rule** (`app/business_rules.py`): status-transition validation
  enforced via an explicit `VALID_TRANSITIONS` set rather than an
  if/elif chain, so the allowed pairs are declarative and easy to audit.
- **Test suite** (`tests/conftest.py`, `tests/test_tasks.py`): 17 pytest
  tests using `TestClient` against the real in-memory store, with an
  `autouse` fixture resetting storage before and after every test.

## How I worked with AI assistance

Each piece was generated from a tightly scoped prompt — one file or one
route at a time — with an explicit checklist to review against before
applying anything (e.g. "does it reject unknown fields," "does a missing
task return 404 before validation runs"). Reviewing against a checklist
before applying caught a real gap: a generated test named
`test_create_task_missing_title_returns_422` sent `{"description": "no
title"}` instead of the empty JSON object the spec called for. The test
still passed, but it wasn't testing what its name claimed — a good
reminder that a passing test isn't automatically a correct test.

## Break testing

I deliberately broke the status-transition rule (commenting out the
`validate_status_transition` call in the PATCH route) and predicted which
tests would fail before running pytest. The result matched the prediction
exactly: only `test_patch_invalid_transition_todo_to_done_returns_422` and
`test_patch_same_status_returns_422` failed, while the other 15 tests were
unaffected. That precise match was useful evidence that the test suite is
actually coupled to the behavior it claims to protect, not just
coincidentally green.

## Debugging friction (environment, not code)

Most of the actual debugging time went into PowerShell/curl quoting, not
the application logic:
- `curl` in PowerShell resolves to `Invoke-WebRequest`, not real curl —
  needed `curl.exe` explicitly.
- Escaped double quotes in `-d` JSON payloads got mangled by PowerShell's
  argument re-encoding; the `--%` stop-parsing token was the reliable fix.
- Running `pytest` directly failed with `ModuleNotFoundError: No module
  named 'app'` because the plain `pytest` script doesn't add the current
  directory to `sys.path`; `python -m pytest` fixed it.
- A manual edit during the break-test exercise introduced an indentation
  mismatch, which surfaced as a Python `IndentationError` at import time
  rather than a normal test failure — a useful distinction between
  "the code is broken" and "the code won't even load."

## Open item carried forward

Module 1's `CONTEXT.md` documents that a task with status `Done` cannot
transition back to `ToDo` or `InProgress`. The Module 2 spec I implemented
against explicitly allows `Done → InProgress` in `VALID_TRANSITIONS`. I
flagged this conflict when it came up rather than silently picking one —
it's still unresolved and worth deciding on explicitly before the midterm
folder is assembled.
