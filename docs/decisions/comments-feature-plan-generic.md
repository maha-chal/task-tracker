# Comments on Tasks — Generic Plan (baseline)

A generic, code-free plan for adding comments to tasks, produced **without
reading the repository**. It is framework- and repo-agnostic and makes no claims
about actual file names, storage, frontend structure, or test style. Kept as the
baseline for comparison against the repo-grounded plan in
`comments-feature-plan.md`.

## 1. Data Model

A new `Comment` entity, separate from the task entity, with a many-to-one
relationship (many comments belong to one task).

Fields (per spec):

| Field | Type | Rules |
|---|---|---|
| `id` | string (UUID) | Server-generated; unique; primary identifier. |
| `task_id` | string | Reference to an existing task; must point to a task that exists. |
| `author` | string | Required; length 1–100 chars (trimmed length is the fairest thing to validate). |
| `body` | string | Required; length 1–2000 chars (trimmed). |
| `created_at` | datetime (UTC) | Server-generated at creation; not client-supplied. |

Modeling decisions to make explicit:
- **Ownership / lifecycle:** decide whether deleting a task also deletes its comments (cascade) or is blocked while comments exist. *(Assumption below: cascade.)*
- **Immutability:** the spec lists no `updated_at` and no editor field, so this plan treats comments as **create/read/delete only** (no edit). Flagged as an open question.
- **Ordering:** comments are most useful returned oldest→newest by `created_at`; `created_at` should therefore be reliable and monotonic enough to sort by.

## 2. API Routes

A comments collection nested under a task, which keeps the parent relationship
explicit:

| Method | Path | Purpose | Success | Notable errors |
|---|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | Create a comment on a task | 201 + created comment | 404 if task missing; 422 if `author`/`body` fail validation |
| `GET` | `/tasks/{task_id}/comments` | List a task's comments | 200 + list (possibly empty) | 404 if task missing |
| `GET` | `/comments/{id}` *(optional)* | Fetch one comment | 200 | 404 if missing |
| `DELETE` | `/comments/{id}` *(or nested)* | Remove a comment | 204 no content | 404 if missing |

Route-level rules:
- **Server owns `id` and `created_at`** — reject or ignore them if sent in the body.
- **Validation on create:** required `author` (1–100) and `body` (1–2000); reject unknown fields to stay strict.
- **Parent existence:** creating/listing under a non-existent `task_id` returns 404, not an empty success.
- **Empty list is a 200**, not a 404 — "task exists but has no comments" is a valid state.
- Whether to expose the flat `GET /comments/{id}` vs. only nested routes is a style choice (open question).

## 3. Tests

Cover behavior, not implementation. Grouped by route:

**Create**
- Valid comment → 201, response echoes `author`/`body`, includes server-set `id` and `created_at`.
- Missing/blank `author` → 422; missing/blank `body` → 422.
- `author` at 100 chars OK, 101 → 422; `body` at 2000 OK, 2001 → 422 (boundary tests).
- Whitespace-only `author`/`body` → 422 (if trimming is the rule).
- Unknown field in body → 422 (if strict).
- Comment on non-existent task → 404.
- Client-supplied `id`/`created_at` ignored or rejected.

**List**
- Task with no comments → 200 + empty list.
- Task with several → 200, all returned, in a defined order (e.g., oldest→newest).
- List for non-existent task → 404.

**Delete** *(if included)*
- Existing comment → 204, and a subsequent fetch/list no longer shows it.
- Non-existent comment → 404.

**Relationship**
- Deleting a task with comments behaves per the chosen lifecycle rule (cascade removes them, or is blocked) — one test asserting whichever you pick.

## 4. Frontend Changes

Described generically, since the UI structure is unknown:

- **Display:** show a comment count and/or a comments area on each task's detail or card view.
- **List rendering:** render each comment's `author`, `body`, and a human-readable `created_at`, in the same order the API returns.
- **Create form:** an input for `author` and a multi-line input for `body`, with client-side length hints (1–100 / 1–2000) mirroring server limits — client validation is UX only; the server remains the source of truth.
- **Safety:** render `author`/`body` as **text, not HTML**, so user-entered content can't inject markup.
- **States:** handle loading, empty ("no comments yet"), and error (failed create/list) states.
- **Refresh:** after a successful create, re-fetch or optimistically append so the new comment appears.

## 5. Migration or Data-Shape Notes

- **New collection/table/store** for comments, plus an index or lookup path on `task_id` for efficient listing. *(Exact mechanism depends on storage — assumption below.)*
- **If storage is persistent (DB):** a schema migration adds the comments table and a foreign key / index on `task_id`; decide on-delete behavior (cascade vs. restrict) at the schema level.
- **If storage is in-memory/ephemeral:** no migration artifact is needed; you add a new in-memory structure keyed for `task_id` lookup, and existing data is unaffected because comments are additive.
- **Backward compatibility:** adding comments is **purely additive** — existing tasks and their responses are unchanged unless you choose to embed a comment count in the task payload (a separate, optional decision).
- **Serialization:** ensure `created_at` is emitted in a consistent UTC format matching whatever the rest of the API already uses.

## 6. Open Questions

1. **Edit support?** Spec has no `updated_at`/editor — are comments truly immutable (no `PATCH`)?
2. **Delete semantics:** hard delete vs. soft delete? Who is allowed to delete (no auth/authorization is specified)?
3. **Task deletion → comments:** cascade delete, or block/restrict?
4. **Authorization:** is `author` a free-text label the client sends, or derived from an authenticated identity? (Affects trust in the field.)
5. **Route shape:** nested-only (`/tasks/{id}/comments`) vs. also flat (`/comments/{id}`)?
6. **Pagination/limits:** any cap on comments per task, or page size for listing?
7. **Ordering contract:** is oldest→newest the guaranteed order, and is `created_at` precise enough to sort ties?
8. **Uniqueness/rate:** any rule against duplicate or rapid-fire identical comments?

---

## Assumptions this plan makes

- **Assumption — relationship:** comments relate to tasks many-to-one via `task_id`; a comment cannot exist without a valid parent task.
- **Assumption — no edit:** comments are create/read/delete only, because the spec includes no `updated_at` or editor field. (Open question #1.)
- **Assumption — cascade on task delete:** deleting a task deletes its comments. (Open question #3 — could be the opposite.)
- **Assumption — validation is on trimmed length**, and blank/whitespace-only `author`/`body` are invalid.
- **Assumption — server authority:** `id` and `created_at` are always server-generated and never trusted from the client.
- **Assumption — `author` is a client-supplied string**, not an authenticated identity (no auth was specified). (Open question #4.)
- **Assumption — nested route shape** (`/tasks/{task_id}/comments`) is the primary design; the flat `/comments/{id}` route is optional.
- **Assumption — empty list is a valid 200 response**, distinct from a 404 for a missing task.
- **Assumption — additive change:** existing task data and responses are unaffected; no task backfill is required.
- **Assumption — storage-agnostic:** the store may be a database or in-memory, so Section 5 gives both paths rather than one.
- **Assumption — generic test style:** the test list describes *what* to assert (status codes, boundaries, relationships), not a specific framework or file layout.
- **Assumption — generic frontend:** the UI structure is unknown, so Section 4 describes behavior and states, not components or files.

---

## Note on use

This is the **generic baseline**. Where it differs from the repo-grounded plan
(`comments-feature-plan.md`) is exactly where reading the repo added value —
notably: actual storage is in-memory (no DB/migration), the frontend is a
single-file board (no detail view), routes are otherwise flat, delete has no
cascade today, and the test command / CI are pinned to a specific test file.
