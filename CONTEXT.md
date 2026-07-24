# Task Tracker — Project Context (Module 2)

This file summarizes the decisions and requirements established for this
project so far, for anyone (human or AI) picking up the codebase without
prior context. For the original Module 1 version of this document, see
[CONTEXT_v0.md](CONTEXT_v0.md).

## What this project is

A Task Tracker REST API built with Python and FastAPI, as a learning
project (AUB AI-Assisted Coding course, Module 1). Tasks have: `id`,
`title`, `description`, `status`, `priority`, `assignee`.

## Explicitly out of scope for Module 1

Authentication, user accounts, admin roles, multi-tenancy, per-user task
lists, real-time updates, mobile app, notifications, production database,
and deployment.

## Requirements

- **Create task**: title required (non-empty after trimming whitespace);
  missing/blank/whitespace-only title returns HTTP 422 with detail
  "Title is required and cannot be blank". `description` and `assignee`
  are optional.
- **View all tasks**: returns full list; empty list (not an error) if no
  tasks exist.
- **Filter tasks**: by `status` and/or `priority`, combinable with AND
  logic. Invalid filter values return HTTP 422.
- **View one task**: by id; HTTP 404 if the id doesn't exist.
- **Update task**: partial update (only sent fields change). Invalid
  `status`/`priority` values return HTTP 422, no change persisted.
  Updating a non-existent id returns HTTP 404.
- **Business rule**: status transitions are restricted to an explicit
  allow-list: `ToDo → InProgress`, `InProgress → Done`, and
  `Done → InProgress`. Any other transition (including same-status, e.g.
  `ToDo → ToDo`) returns HTTP 422 with a clear invalid-transition message;
  the task's status is unchanged. **Note:** this differs from the
  Module 1 draft of this rule (see CONTEXT_v0.md), which stated `Done`
  could not transition back to `InProgress` at all. The Module 2 prompt
  spec explicitly allows `Done → InProgress`, and the implementation
  follows that spec. This conflict has not been resolved with the course
  instructor as of this writing.
- **Delete task**: removes the task, returns HTTP 204. Deleting a
  non-existent id returns HTTP 404.
- **Enums**:
  - `status`: `ToDo`, `InProgress`, `Done`
  - `priority`: `Low`, `Medium`, `High`
- `assignee` is a plain text label — not linked to authentication or
  user accounts.

## Architecture Decision Records

### ADR-001: Task Storage Approach

**Decision:** Use an in-memory data store (a Python dictionary) for
Module 1, instead of a real database like SQLite.

**Why:** This is a learning project focused on understanding how a REST
API works — creating, reading, updating, and deleting tasks. Adding a
real database at this stage would introduce extra complexity (setup,
queries, schema management) before the core API concepts are solid.

**Trade-off accepted:** All tasks are lost when the application
restarts. This is acceptable for Module 1, since the priority is
understanding the API itself, not data persistence.

**Alternative considered:** A SQLite database, which would keep data
between restarts and better resemble a real-world project. This was set
aside for now to keep the learning curve manageable, but may be
revisited in a later module.

### ADR-002: Testing Approach

**Decision:** Write tests directly against the in-memory store, with no
separate test database.

**Why:** This keeps testing simple and approachable while still building
the habit of writing tests early. It avoids adding database
setup/teardown complexity while foundational testing skills are still
being learned.

**Trade-off accepted:** These tests won't teach database-specific
testing practices (e.g., isolating a test database, managing fixtures).
That gap is acceptable for now and can be addressed in a future project
once database use is introduced.

**Alternative considered:** Using a real (test) database with fixtures
for more realistic testing. This was set aside to avoid layering two new
skills (testing and database management) at once.

## Current implementation status

- `app/main.py` implements all five task routes: `POST /tasks`,
  `GET /tasks` (with optional `status`/`priority` filters),
  `GET /tasks/{task_id}`, `PATCH /tasks/{task_id}`, and
  `DELETE /tasks/{task_id}`, alongside the original `GET /health`.
- `app/models.py` defines `TaskStatus`, `TaskPriority`, `TaskCreate`,
  `TaskUpdate`, and `TaskResponse` (Pydantic v2, `extra="forbid"` on all
  request/response models).
- `app/storage.py` implements the in-memory store (`_tasks` dict) with
  `add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`,
  `delete_task`, and a test-only `_reset`.
- `app/business_rules.py` implements status-transition validation via an
  explicit `VALID_TRANSITIONS` frozenset (see the Business rule note
  above for the Module 1/2 discrepancy).
- `tests/conftest.py` and `tests/test_tasks.py` contain a 17-test pytest
  suite covering all five routes, validation errors, and transition
  rules, run against the real in-memory store via `TestClient` with an
  autouse reset fixture. Run with `python -m pytest tests/test_tasks.py -v`
  (plain `pytest` fails with `ModuleNotFoundError: No module named 'app'`
  since it doesn't add the project root to `sys.path`).
- Project uses: FastAPI, Uvicorn, Pydantic, python-dotenv (dotenv not yet
  wired up to actually load `.env` values), plus `pytest` and `httpx` for
  testing (not yet added to `requirements.txt`).

## AI-assumption corrections made during planning

- An earlier draft assumed frontend "feedback on failure" implied a
  notification system; this was corrected to mean an inline UI error
  message, since notifications are out of scope.
- `assignee` was clarified as a plain text field, not linked to user
  accounts, to avoid it being mistaken for an authentication-adjacent
  feature.
