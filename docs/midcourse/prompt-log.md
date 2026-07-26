# Prompt Log — Mid-Course Project

For each prompt: what was asked, what the AI returned, and what was accepted, edited, or
rejected. Full prompt text for each of these lives in this conversation; summarized here for
readability.

## Feature 1: Due dates + overdue filter

### Prompt 1 — `app/models.py`: add `due_date`
Asked for `due_date: date | None` on `TaskCreate`/`TaskUpdate`/`TaskResponse`, using Pydantic's
native `date` type for `YYYY-MM-DD` format enforcement, no custom validator.
- **Returned:** exactly as asked — `due_date` added to all three models, no validator.
- **Edited before implementing:** rejected the "no custom validator" instruction after separately
  verifying (via a direct Python check) that Pydantic's native `date` type silently accepts an
  int/float as a Unix timestamp instead of returning 422. Added a `field_validator(mode="before")`
  rejecting non-`str`/non-`None` input before this was implemented — a correction to the plan, not
  the AI's returned code, since the gap was caught before the first draft was even written to disk.

### Prompt 2 — `app/storage.py`: wire `due_date` + `is_overdue`
Asked to persist `due_date` in `add_task`, add `is_overdue(task)`, and extend `get_all_tasks` with
an `overdue` filter; explicitly asked to *verify, not assume* whether `update_task` needed changes.
- **Returned:** all three changes, plus a one-line confirmation that `update_task` needed no
  changes (already correct via `exclude_unset` + `model_copy`).
- **Accepted as-is**, after independently re-verifying the "no changes needed" claim with a
  manual script (omit/explicit-null/Done-exclusion checks) rather than trusting the claim alone.

### Prompt 3 — `app/main.py`: expose `overdue` query parameter
Asked for the one-line route change, plus justification for why the other four routes needed
no changes.
- **Returned:** the `list_tasks` change and the justification.
- **Accepted as-is**; regression-tested against the full suite before moving on.

### Prompt 4 — pytest tests for `due_date`/overdue
Asked for tests covering creation, update, and the overdue filter, using relative dates
(`timedelta`) instead of a time-freezing library, per the mini-ADR decision.
- **Returned:** 14 tests.
- **Accepted as-is** after running the full suite (32 passed) to confirm no regressions.

### Prompt 5 — frontend: due date input, display, overdue class, filter toggle
Asked for the modal field, card display, `isOverdue()`/`todayIsoString()` (explicitly specifying
local date components, not `toISOString()`, to avoid a UTC-shift bug), and a filter toggle.
- **Returned:** all pieces as specified.
- **Accepted as-is**, verified via direct JS execution against the live page (bypassing a known
  sandbox limitation where the embedded browser pane can't reach locally-started backend servers).

## Feature 2: Tags / labels

### Prompt 1 — `app/models.py`: add `tags`
Asked for `tags: list[str]` with a validator (trim, reject blank, case-insensitive dedup),
explicitly no comma-parsing at the model layer.
- **Returned:** exactly as asked.
- **Accepted as-is**, verified manually (dedup order/casing, default empty list, blank rejection).

### Prompt 2 (weak) → Prompt 2 (rewritten, stronger) — `app/storage.py`: wire `tags`
The first draft of this prompt only asked to persist `tags` in `add_task` and verify
`update_task` — it did **not** include a tag filter, even though the original feature brief
mentioned "tag filtering or search by tag" as expected frontend work. This was a weak prompt: it
would have produced working code that silently omitted a real, briefed requirement.
- **What made it weak:** it was scoped to only what `user-stories.md` explicitly covered at the
  time, but `user-stories.md` itself had a gap (never turned "filter by tag" into a story).
- **Rewrite:** rather than just adding the filter to the storage prompt, first added **Story 7**
  (filter by tag) and **Story 8** (update tags — replace, not merge) to `user-stories.md`, *then*
  rewrote the storage prompt to explicitly reference both stories and require the `tag` parameter.
- **Returned (final version):** `tags` persisted, a case-insensitive `tag` filter with AND-logic
  combination, and confirmation that `update_task` already satisfied all three tag-update cases.
- **Accepted as-is**, verified manually for all cases including the AND-logic combination.

### Prompt 3 — `app/main.py`: expose `tag` query parameter
Same shape as Feature 1's route prompt.
- **Returned:** the one-line `list_tasks` change plus justification.
- **Accepted as-is.**

### Prompt 4 — pytest tests for tags/tag filter
Asked for tests covering creation, update (replace/omit/clear), and the tag filter (including
AND-logic with `status`).
- **Returned:** 13 tests.
- **Accepted as-is**; full suite reached 45 passed.

### Prompt 5 — frontend: tags input, chip display, tag filter
Asked for a comma-separated tags field (per the locked-in simplest-option decision over an
interactive chip widget), conditional chip rendering, and a `URLSearchParams`-based rewrite of
`fetchTasks` so the tag and overdue filters could combine.
- **Returned:** all pieces as specified.
- **Accepted as-is**, verified via direct JS execution (chip rendering, modal prefill, tag-parsing
  edge cases including messy comma/space input).
