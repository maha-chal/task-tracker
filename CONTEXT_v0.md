# Task Tracker — Project Context (Module 1)

> **Archived snapshot — not current.** This is the Module 1 version of
> this document, preserved unchanged for reference. It does **not**
> reflect the real, current routes, models, storage layer, business
> rules, or test suite implemented in Module 2 (e.g. its "Current
> implementation status" section below still describes a health-check-only
> skeleton with no CRUD routes). Its stated business rule below — "a task
> with status `Done` cannot transition back to `ToDo` or `InProgress`" —
> also conflicts with what was actually implemented in Module 2: the
> `VALID_TRANSITIONS` set in `app/business_rules.py` explicitly allows
> `Done → InProgress` (only `Done → ToDo` and same-status transitions are
> rejected). This conflict is unresolved as of this writing. See
> [CONTEXT.md](CONTEXT.md) for the up-to-date version.

This file summarizes the decisions and requirements established for this
project so far, for anyone (human or AI) picking up the codebase without
prior context.

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
- **Business rule**: a task with status `Done` cannot transition back to
  `ToDo` or `InProgress`. Attempting this returns HTTP 422 with a clear
  invalid-transition message; the task's status is unchanged.
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

- `app/main.py` currently contains **only** a `GET /health` endpoint
  (returns `{"status": "ok", "timestamp": "..."}`, HTTP 200). This was a
  deliberate scaffold-first step, reviewed and confirmed safe to build on.
- CRUD endpoints (create/list/get/update/delete tasks) matching the
  requirements above have **not yet been added back** to this file and
  are the next step.
- Project uses: FastAPI, Uvicorn, Pydantic, python-dotenv (dotenv not
  yet wired up to actually load `.env` values).
- Storage layer (`TaskStore` in-memory dict) and Pydantic models
  (`TaskStatus`, `TaskPriority`, `Task`, `TaskCreate`, `TaskUpdate`) were
  previously built and tested in an earlier version of this project, but
  are not currently present in the skeleton — they need to be
  re-added/rebuilt to match the requirements above (including the new
  Done → ToDo/InProgress transition rule, which was not in the original
  version).

## AI-assumption corrections made during planning

- An earlier draft assumed frontend "feedback on failure" implied a
  notification system; this was corrected to mean an inline UI error
  message, since notifications are out of scope.
- `assignee` was clarified as a plain text field, not linked to user
  accounts, to avoid it being mistaken for an authentication-adjacent
  feature.
