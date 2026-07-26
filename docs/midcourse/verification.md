# Verification — Mid-Course Project

## Baseline check (before any midterm code changes)

Run on the `mid-course-project` branch, immediately after creating it, before any feature code
was written:

- `python -m pytest tests/test_tasks.py -v` → **18 passed, 0 failed** (4 unrelated
  `StarletteDeprecationWarning` notices only).
- `GET /health` → `200 {"status":"ok",...}`.
- `GET /tasks` → `200`, returning existing task data from prior manual testing.

This confirms a clean, working starting point before any midterm feature work began.

## Backend test results

| Stage | Command | Result |
|---|---|---|
| Baseline | `python -m pytest tests/test_tasks.py -v` | 18 passed |
| After Feature 1 (due dates + overdue filter) | `python -m pytest tests/test_tasks.py -v` | **32 passed** (18 baseline + 14 new) |
| After Feature 2 (tags/labels) | `python -m pytest tests/test_tasks.py -v` | **45 passed** (32 + 13 new) |

Feature 1's 14 new tests cover: creation with a valid/omitted/invalid-format/numeric/past due
date; update with partial change, omitted-vs-null, and invalid-format atomicity; and the overdue
filter (past-due inclusion, future/null exclusion, `Done`-status exclusion, unfiltered `GET`
returning everything regardless of overdue state).

Feature 2's 13 new tests cover: creation with valid/omitted/trimmed/blank/duplicate tags; update
with replace (Story 8), omit-preserves (Story 6), explicit-clear (Story 6), and blank-tag
atomicity (Story 5); and the tag filter (case-insensitive match, no-match empty list, unfiltered
`GET`, and AND-logic combination with `status`).

## Manual browser checks

**Feature 1 (due dates + overdue filter):**
- `isOverdue()`/`todayIsoString()` executed directly against the live page with constructed task
  data: an overdue task (`due_date` in the past, `status: "ToDo"`) → `true`; a future-due task →
  `false`; a task with no due date → `false`; a `Done` task with a past due date → `false`
  (status exclusion confirmed).
- `renderBoard()` called with the same constructed data: the overdue task's card received
  `class="task-card overdue"`; the other cards stayed plain `"task-card"`. The due-date line
  rendered on every card that had one (including the overdue-but-`Done` one, which correctly
  showed the date without the red border), and was absent for the no-due-date task.
- `openModal('create')` leaves the due-date input empty; `openModal('edit', task)` correctly
  pre-fills it from `task.due_date`.
- **Known limitation:** the live `fetch`-based round trip (clicking "Show overdue only" against
  real backend data) could not be verified in this session's embedded Browser pane, since it
  cannot reach backend servers started via this session's own background tooling — a sandbox
  networking gap unrelated to the application code. Recommend a quick manual confirmation in a
  real browser, where this backend has reliably been reachable all session.

**Feature 2 (tags/labels):**
- `renderBoard()` called with constructed task data: a tagged task's card rendered exactly one
  `.tag-chip` element per tag with the correct text; an untagged task's card had no `.task-tags`
  container at all (conditional append confirmed).
- `openModal('edit', task)` correctly pre-fills the tags input as `"urgent, backend"`;
  `openModal('create')` leaves it empty.
- The submit handler's tag-parsing logic (split on comma, trim, filter empty) was executed
  directly: `"urgent, backend, review"` → 3 clean tags; messy input with extra commas/spaces
  (`"  urgent ,, backend ,  "`) → correctly collapsed to `["urgent", "backend"]`; empty string →
  `[]`.
- **Known limitation:** same as Feature 1 — the live `fetch`-based round trip (typing into the tag
  filter input against real backend data) could not be verified in this session's embedded
  Browser pane, for the same sandbox networking reason. Recommend a quick manual confirmation in a
  real browser.

## Break Test evidence

**1. Combined title + invalid status transition (business logic, pre-midterm methodology reused)**
- Target: `test_patch_combined_title_change_with_invalid_transition_returns_422_and_title_unchanged`.
- Break: reordered `app/main.py`'s PATCH route so `storage.update_task(...)` ran *before*
  `validate_status_transition(...)`, instead of after.
- Prediction: `response.status_code == 422` would still pass; the title-unchanged assertion would
  fail, since the write would happen before the (now-late) rejection.
- Actual: exactly as predicted — `assert 'New title' == 'fixture task'` failed, proving the title
  was written to the store before the transition check rejected the request.
- Reverted; suite back to fully passing.

**2. `is_overdue()`'s `Done`-status exclusion (Feature 1 business logic)**
- Target: `test_list_tasks_overdue_filter_excludes_done_task_with_past_due_date`.
- Break: removed the `and task.status != TaskStatus.DONE` clause from `is_overdue()` in
  `app/storage.py`.
- Prediction: only this one test would fail; the other 31 would be unaffected.
- Actual: exactly as predicted — `1 failed, 31 passed`. The failure showed the `Done` task's own
  id appearing in the `?overdue=true` results, proving the test genuinely catches the regression.
- Reverted; suite back to `32 passed`.

**3. Story 8 "replace, not merge" for tag updates (Feature 2 business logic)**
- Target: `test_patch_tags_replaces_existing_set`.
- Break: `update_task` merges new tags with existing ones instead of replacing, whenever the new
  `tags` value is non-empty (a plausible "helpful" bug — preserving old tags rather than
  overwriting them).
- Prediction: only this one test would fail; `test_patch_explicit_empty_tags_clears_them` and
  `test_patch_omitting_tags_leaves_them_unchanged` would be unaffected, since the merge only
  triggers when the new `tags` value is truthy.
- Actual: exactly as predicted — `1 failed, 44 passed`. The failure showed
  `['urgent', 'frontend', 'review']` instead of `['frontend', 'review']` — the old tag leaked
  through, proving the test genuinely catches a merge-instead-of-replace regression.
- Reverted; suite back to `45 passed`.

**4. Tag filter's AND-logic combination with other filters (Feature 2 business logic)**
- Target: `test_list_tasks_filter_by_tag_and_status_combines_with_and_logic`.
- Break: the tag filter in `get_all_tasks` re-scanned the full `_tasks.values()` instead of
  continuing to narrow the already-filtered `tasks` variable — a classic wrong-variable bug that
  silently discards any `status`/`priority`/`overdue` filtering applied earlier in the same call.
- Prediction: only this one test would fail; the two single-filter tag tests would be unaffected,
  since `tasks` and `_tasks.values()` are identical when no other filter is combined.
- Actual: exactly as predicted — `1 failed, 44 passed`. The failure showed both the matching
  (`InProgress`) task and the non-matching (`ToDo`) task returned (2 instead of 1), proving the
  `status` filter was silently discarded once the tag filter re-scanned the full unfiltered set.
- Reverted; suite back to `45 passed`.

## Behavior contract before/after refactor

**Refactor:** extracted the create/edit modal's inline payload-construction logic (title trim,
assignee/due_date null-conversion, tag parsing, conditional `status` inclusion) out of the
`taskForm` submit handler into its own `buildTaskPayload(isEdit)` function in `frontend/index.html`
— the same extract-a-helper pattern already used for `createTaskTitleEl`/`createTaskMetaEl`/etc.
No behavior was intended to change; only where the logic lives.

**Method:** captured the exact payload produced for 3 representative scenarios *before* the
refactor (by executing the literal pre-refactor inline logic against constructed form input), then
reloaded the page after the refactor and called the new `buildTaskPayload(isEdit)` directly against
the same 3 scenarios.

| Scenario | Description |
|---|---|
| A | Create, minimal fields (empty description/assignee/due_date/tags) |
| B | Edit, no status change (title/description/priority/assignee/due_date/tags all populated) |
| C | Edit, status changed (same as B, but with a different `status` value than `originalStatus`) |

**Result:** `JSON.stringify(afterResults) === JSON.stringify(beforeResults)` → **`true`** — all
three scenarios produced byte-for-byte identical payloads before and after the refactor, including
the conditional `status` key being present in A and C but correctly absent in B.

**Backend regression check:** unaffected by this frontend-only refactor, but re-run anyway —
`python -m pytest tests/test_tasks.py -v` → **45 passed**, unchanged.
