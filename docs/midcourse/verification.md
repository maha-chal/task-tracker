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
| After Feature 2 (tags/labels) | *(pending)* | *(pending)* |

Feature 1's 14 new tests cover: creation with a valid/omitted/invalid-format/numeric/past due
date; update with partial change, omitted-vs-null, and invalid-format atomicity; and the overdue
filter (past-due inclusion, future/null exclusion, `Done`-status exclusion, unfiltered `GET`
returning everything regardless of overdue state).

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

**Feature 2 (tags/labels):** *(pending — not yet implemented)*

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

## Behavior contract before/after refactor

*(Pending — no refactor pass has been performed on the midterm feature code yet. This section
will be completed once a refactor is done on Feature 1 and/or Feature 2, following the same
before/after comparison method already used earlier in this project on `renderBoard`/
`createTaskCard`.)*
