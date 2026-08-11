# Comments on Tasks — Feature Plan

Design document (planning only; no implementation).

Scope reminder from the repo: this is a **local, single-user, in-memory, no-auth**
course project (`README.md:12-14`, `AGENTS.md:8-12`). This plan follows the
existing Task patterns rather than introducing new infrastructure.

## Decisions (resolved 2026-08-11)

These resolve Open Questions 1–3 and update Sections 1, 2, and 5.

1. **Route shape → nested.** Comments live at `/tasks/{task_id}/comments`
   (create/list) and `/comments/{comment_id}` (get/edit/delete). Accepted as a
   deliberate deviation from the repo's otherwise-flat routes.
2. **Editable, with an "edited" indicator.** Comments can be updated after
   creation, and the API/UI must show a comment was edited. This adds:
   a `CommentUpdate` model and a **`PATCH`** route (reuses the already-allowed CORS
   `PATCH`); and an **`updated_at`** field on `CommentResponse`, set equal to
   `created_at` on creation and refreshed on edit — mirroring `TaskResponse`
   (`app/models.py:121-122`) and `storage.update_task` (`app/storage.py:124`).
   "Edited" = `updated_at > created_at`. **Sub-decisions — locked (2026-08-11):**
   (a) "edited" is **derived** from `updated_at` — **no separate `edited` boolean**;
   (b) editable fields = **body only** (`author`/`created_at` stay immutable).
   *Minimal footprint:* every backend piece mirrors an existing task function, and
   the `PATCH` handler is `update_task` **minus** the status-transition check
   (`app/main.py:166-170`). `updated_at` is the single field added beyond the
   original comment spec.
3. **Cascade on task delete.** Deleting a task also deletes its comments —
   `storage.delete_task` (`app/storage.py:130-142`) gains explicit cascade code;
   new behavior, since no cascade exists today.

## 1. Data Model

**Where:** `app/models.py`, alongside the existing task models, which use a
three-model split (`TaskCreate` / `TaskUpdate` / `TaskResponse`, `app/models.py:20-123`).

Proposed models, mirroring that split:

- **`CommentCreate`** — client input: `author`, `body` only.
- **`CommentResponse`** — full record: `id`, `task_id`, `author`, `body`, `created_at`, `updated_at` (see Decisions §2).
- **`CommentUpdate`** — editable **body only**; comments carry `updated_at` so an edit is visible (Decisions §2). `author` and `created_at` stay immutable.

**Fit with existing conventions:**

| Concern | Existing task convention (observed) | Applied to comments |
|---|---|---|
| Strictness | `model_config = ConfigDict(extra="forbid")` on every model (`app/models.py:21,64,111`) | Same — unknown fields → 422 |
| Field validation | `@field_validator` classmethods raising `ValueError`; `validate_title` trims and caps at 200 (`app/models.py:31-39`) | `author` trimmed, 1–100; `body` trimmed, 1–2000 — same validator style |
| `id` | `str(uuid.uuid4())` set in storage (`app/storage.py:23-24`) | Same |
| `created_at` | `datetime.now(timezone.utc)` set in storage (`app/storage.py:22,32`) | Same; server-generated, never from client |
| Enums / rules | Domain rules live in `app/business_rules.py` | Comments have no state machine, so no business-rules addition |

**Note on validation consistency:** capping `author`/`body` would make comments
*stricter* than existing task fields — `description` and `assignee` are currently
**uncapped** (`app/models.py:24,27`; this is finding V-1 in `docs/security-review.md`).
So this feature introduces the length-cap pattern the task model only partially
follows. Decision point (Open Questions).

**Persistence shape:** `app/storage.py` currently holds tasks in a module-level
`_tasks: dict[str, TaskResponse]` (`app/storage.py:7`) with `add_task`,
`get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`, and `_reset`.
Comments would add a parallel `_comments` dict plus mirror functions
(`add_comment`, `get_comments_for_task`, `get_comment_by_id`, `delete_comment`).
**`_reset()` (`app/storage.py:145-146`) must also clear `_comments`** — the test
suite's autouse fixture depends on `_reset` (`tests/conftest.py:8-12`).

## 2. API Routes

Existing routes are **flat** (`/tasks`, `/tasks/{task_id}`, `app/main.py:51-198`),
all tagged `tags=["tasks"]`, with a fixed 404 pattern:
`HTTPException(status_code=404, detail=f"Task with id {task_id} not found")`.
Comments are a sub-resource, so nesting under the task is proposed (with a caveat
in Open Questions, since the repo has no nesting precedent).

| Method | Path | Request body | Success response | Error cases |
|---|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | `author`, `body` | **201** + `CommentResponse` | 404 if task not found (reuse existing detail wording); 422 on blank/oversized `author`/`body` or unknown field |
| `GET` | `/tasks/{task_id}/comments` | — | **200** + list of `CommentResponse` (empty list allowed) | 404 if task not found |
| `GET` | `/comments/{comment_id}` *(optional)* | — | **200** + `CommentResponse` | 404 if comment not found |
| `PATCH` | `/comments/{comment_id}` | `body` | **200** + `CommentResponse` (with refreshed `updated_at`) | 404 if comment not found; 422 on blank/oversized `body` or unknown field |
| `DELETE` | `/comments/{comment_id}` | — | **204** no content | 404 if comment not found |

Conventions carried over:
- `response_model=CommentResponse` / `list[CommentResponse]`, `status_code` set explicitly (201, 204) as tasks do (`app/main.py:51,178`).
- New `tags=["comments"]` group for the Swagger UI (`README.md:25`).
- **`PATCH`** (comment editing) reuses the already-allowed CORS `allow_methods` (`GET, POST, PATCH, DELETE`, `app/main.py:23`), so **no CORS change is needed** for any comment route. The `PATCH` handler refreshes `updated_at`, mirroring `storage.update_task` (`app/storage.py:124`).

## 3. Tests

**Style (observed):** `tests/test_tasks.py` uses the `client` and `created_task`
fixtures and an autouse `_reset_storage` (`tests/conftest.py`), with names like
`test_<action>_<condition>_returns_<code>`. A new `tests/test_comments.py` would
follow the same shape and reuse those fixtures.

**Concrete test names:**

*Happy path*
- `test_create_comment_valid_returns_201_with_full_body`
- `test_list_comments_returns_all_for_task`
- `test_list_comments_empty_returns_200_and_empty_list`
- `test_delete_comment_returns_204_no_body`

*Validation*
- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_over_100_chars_returns_422`
- `test_create_comment_author_at_100_chars_returns_201` (boundary)
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_over_2000_chars_returns_422`
- `test_create_comment_body_at_2000_chars_returns_201` (boundary)
- `test_create_comment_unknown_field_returns_422`

*Editing*
- `test_patch_comment_updates_body_returns_200`
- `test_patch_comment_refreshes_updated_at_and_marks_edited`
- `test_patch_comment_not_found_returns_404`
- `test_patch_comment_blank_or_oversized_body_returns_422`
- `test_patch_comment_cannot_change_author_or_created_at`

*Edge cases*
- `test_create_comment_on_missing_task_returns_404`
- `test_list_comments_on_missing_task_returns_404`
- `test_get_comment_not_found_returns_404`
- `test_delete_comment_not_found_returns_404`
- `test_create_comment_ignores_client_supplied_id_and_created_at`
- `test_comments_are_isolated_between_tasks`
- `test_delete_task_behavior_for_its_comments` (asserts whichever cascade/orphan rule is chosen)

**Important CI catch:** the test command and CI both name `tests/test_tasks.py`
**explicitly**, not the `tests/` directory (`README.md:118,158-159`;
`.github/workflows/ci.yml:25`). A new `tests/test_comments.py` **will not run** in
CI or the documented command until both are updated. (Migration Notes / Open Questions.)

## 4. Frontend Changes

**File:** `frontend/index.html` — a single-file vanilla-JS Kanban board (no
framework/build, `README.md:20`). There is **no task detail page**; tasks are
cards (`createTaskCard`, `frontend/index.html:521`) with a create/edit modal
(`openModal`, `frontend/index.html:708`).

What would change and what the user would see:
- **Where comments live in the UI:** most naturally inside the **edit modal** (a per-task context already exists there), and/or a **comment count badge** on the card. Which one is a design choice.
- **New data calls:** functions mirroring `fetchTasks` (`frontend/index.html:477`), using the existing `API_BASE_URL` (`frontend/index.html:446`), to GET a task's comments and POST a new one.
- **Rendering:** build comment rows with `createElement` + **`textContent`** — matching the existing XSS-safe pattern (all task fields render via `textContent`; never `innerHTML` for data, `frontend/index.html:560-608`). This keeps comments consistent with the frontend's clean-XSS posture.
- **Add-comment form:** `author` and `body` inputs with client-side length hints (1–100 / 1–2000) mirroring the server; client validation is UX only — the server stays authoritative.
- **States:** current error handling is minimal (a failed load only `console.error`s, `frontend/index.html:494-496`); comments would reuse the `showMessage` / `showModalError` helpers for empty/error feedback.
- **Container note:** the Docker image copies only `app/` (`README.md:130-131`), so frontend changes don't affect the containerized API.

## 5. Migration Notes

- **No database → no schema migration.** The only storage-shape change is adding a `_comments` dict in `app/storage.py` and its accessor functions.
- **`_reset()` must clear comments** or tests will leak state across cases (autouse fixture, `tests/conftest.py:8-12`).
- **Existing task data is unaffected** — the change is purely additive. Task request/response shapes stay the same *unless* you choose to embed a `comment_count` in the task response (a deliberate, separate change).
- **Cascade on task delete:** `storage.delete_task` (`app/storage.py:130-142`) must gain explicit code to remove a task's comments — new behavior, since no cascade exists today (Decisions §3).
- **Test/CI scope must be widened:** update the pinned `python -m pytest tests/test_tasks.py -v` command (`README.md:118`) and `.github/workflows/ci.yml:25` to include `tests/test_comments.py` (or switch to `tests/`), or the feature ships untested in CI.
- **No new dependencies** — `uuid`, `datetime`, and Pydantic v2 are already in use (`app/storage.py:1-2`, `requirements.txt`).
- **Persistence caveat:** comments are lost on restart, same as tasks. Making them durable would contradict the in-memory decision recorded in `docs/midcourse/mini-adr.md` and the scope note in `README.md:12-14` — out of scope here.

## 6. Open Questions

1. **Route shape:** ✅ **Resolved — nested** `/tasks/{task_id}/comments`; accepted deviation from the flat convention (Decisions §1).
2. **Immutable or editable?** ✅ **Resolved — editable, body-only, with a derived edit indicator** (`updated_at > created_at`, no `edited` flag); adds `CommentUpdate` + `PATCH` (Decisions §2).
3. **Task deletion → its comments:** ✅ **Resolved — cascade-delete** (Decisions §3).
4. **CI/test scope:** will the team update the explicitly-pinned `tests/test_tasks.py` command and `ci.yml` to run comment tests? (Otherwise the feature is unverified in CI.)
5. **Author trust:** with no auth (`README.md:194`), `author` is unauthenticated free text a client can set to anything. Acceptable for this scope, or should it be constrained?
6. **Validation alignment:** capping `author`/`body` is stricter than the uncapped `description`/`assignee` (V-1). Align the task fields too, or accept the inconsistency?
7. **Ordering / limits:** guarantee oldest→newest by `created_at`, and cap comments per task or page the list?

---

## Files read

- `AGENTS.md` — agent contract, Module 5 guardrails (docs-first, no `app/` edits), business-rule summary.
- `app/models.py` — three-model split, `extra="forbid"`, `field_validator` style, `validate_title` cap, uncapped `description`/`assignee`.
- `app/main.py` — flat routes, `response_model`/`status_code`/`tags` decorators, 404 detail pattern, CORS `allow_methods`.
- `app/storage.py` — in-memory `_tasks` dict, uuid/UTC generation, accessor functions, `_reset`.
- `app/business_rules.py` — where domain rules live (status transitions); no comment rule needed.
- `tests/test_tasks.py` — test naming and grouping conventions, boundary/validation/edge patterns.
- `tests/conftest.py` — `client`, `created_task`, autouse `_reset_storage` fixtures.
- `frontend/index.html` — single-file board, `createTaskCard`, `openModal`, `fetchTasks`, `API_BASE_URL`, `textContent` rendering, minimal error handling.
- `README.md` — run/test commands, CI scope pinned to `tests/test_tasks.py`, in-memory/no-auth scope, project structure, Docker copies `app/` only.
- `CLAUDE.md` — stack versions, do-not rules (no DB/auth/deployment without asking).

## Assumptions to verify

- **Decided — comments are editable**, body-only, with a **derived** `updated_at` edit indicator (no `edited` flag); every backend piece mirrors an existing task function (Decisions §2).
- **Decided — nested routes** (Decisions §1), an accepted deviation from the repo's flat convention.
- **Decided — cascade-delete** comments on task delete (Decisions §3); requires new code in `storage.delete_task`.
- **Assumption — `_reset()` will be extended** to clear comments; required for the existing test fixture to keep isolating cases.
- **Assumption — CI/test command will be widened** to include a new test file; otherwise comment tests never run.
- **Assumption — `author` stays unauthenticated free text**, consistent with the no-auth scope.
- **Assumption — comments UI attaches to the edit modal / card**, since there is no detail view; the exact placement is unconfirmed.
- **Assumption — task response shape stays unchanged** (no embedded `comment_count`) unless the team opts in.
- **Not visible from the files:** any product requirement on comment ordering, pagination, per-task limits, or who may delete a comment — none of these are expressed anywhere in the repo, so they must come from the team.
