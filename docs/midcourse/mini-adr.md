# Mini-ADR — Due Dates + Overdue Filter, and Tags / Labels

## Decision

Implement both selected features (Due dates + overdue filter, Tags / labels) using **Option A**:
extend the existing in-memory storage (the `_tasks` dict in `app/storage.py`), rather than
introducing a database.

## Context

The existing Task Tracker (Modules 1-3) uses in-memory storage exclusively, with a FastAPI
backend, Pydantic models, and a vanilla HTML/CSS/JS frontend. The midterm requires adding two
scoped features end-to-end. Two architecture options were evaluated before coding:

- **Option A** — extend the current in-memory dict storage with two new fields.
- **Option B** — introduce SQLite (via stdlib `sqlite3`) as a lightweight local database.

## Alternatives AI suggested

- **Storage:** Option B (SQLite), with `tags` stored as a JSON-encoded text column (SQLite has no
  native array type), `due_date` stored as an ISO date string, and schema auto-created on startup.
- **Timezone handling for `due_date`/overdue:** explicit UTC (`datetime.now(timezone.utc).date()`),
  matching the existing `created_at`/`updated_at` convention already used elsewhere in the app.
- **Tag-input UX:** an interactive chip-input widget (type + Enter to add a chip, click a chip's
  `×` to remove it), as an alternative to a plain text field.
- **Test determinism for overdue logic:** a time-freezing library (e.g. `freezegun`) to pin "today"
  during tests.

## What was rejected, and why

- **Option B (SQLite) rejected.** Given the midterm deadline, Met/Not Met grading based on
  demonstrated AI-assisted workflow (not architectural sophistication), and the fact that all 18
  existing passing tests would need their reset fixture rewritten (`_tasks.clear()` →
  `DELETE FROM tasks` or a fresh `:memory:` connection), the added complexity — a new `db.py`,
  hand-written SQL, manual JSON encode/decode for `tags`, no migration tooling — wasn't justified
  for two small, additive features. This also matches ADR-001 already recorded in `CONTEXT.md`,
  which reasoned through this exact trade-off for the original project and deliberately deferred it.
- **UTC-based due-date comparison rejected**, in favor of a naive server-local date
  (`date.today()`). UTC would be marginally more consistent with existing timestamp fields, but the
  naive approach is simpler to write, and the difference is immaterial for a local, single-server
  project with no user accounts or per-user timezones.
- **Interactive chip-input widget rejected**, in favor of a single comma-separated text field.
  The chip widget would require meaningfully more JavaScript (keydown handling, chip-state-to-array
  sync) for a UX improvement that no acceptance criterion actually requires — tag chips already
  render on the card after saving regardless of how they were typed in.
- **`freezegun` (or similar) rejected**, in favor of computing test dates relative to `date.today()`
  using stdlib `timedelta`. This avoids a new dependency, stays consistent with the naive-date
  decision, and the midnight-boundary flakiness it would guard against is negligible for a fast
  local test suite.

## Accepted trade-offs and known limitations (explicit, not silent)

- Due dates and tags are lost on server restart, same as all other task data — an existing,
  already-documented trade-off (ADR-001), not a new one introduced by these features.
- Tags cannot contain a literal comma, since comma is the input delimiter.
- Overdue calculation uses the server machine's local system clock; this is only acceptable
  because there is no deployment or multi-user timezone concern in scope.
- No maximum tag count or length is enforced, even though the feature brief listed this as
  optional backend work.
- Duplicate tags are silently deduplicated (case-insensitive) rather than rejected — already
  labeled as an assumption not present in the original brief in `user-stories.md`.

## Design (kept small)

- `app/models.py` — add `due_date: date | None = None` and `tags: list[str] = []` to
  `TaskCreate`, `TaskUpdate`, and `TaskResponse`; add a `tags` validator that trims each value,
  rejects blank entries, and deduplicates case-insensitively.
- `app/storage.py` — extend `add_task`/`update_task` to carry the two new fields; add an
  `is_overdue(task)` helper computed at read time (`due_date is not None and due_date < date.today()
  and status != "Done"`); extend `get_all_tasks` with an `overdue: bool | None` filter parameter.
- `app/main.py` — add `overdue: bool | None = None` as a query parameter on `GET /tasks`.
- `frontend/index.html` — add a due-date input and a comma-separated tags text input to the
  create/edit modal; render `.task-due-date` and `.tag-chip` elements on cards; apply an
  `overdue` class to qualifying cards; add an overdue filter toggle to the board.
- No new files and no new dependencies, frontend or backend.

## Implementation summary

Both features were implemented in the same small-step order for each: models → storage → route →
tests → frontend, verifying each layer (manual sanity checks and/or the full pytest suite) before
moving to the next, per the recommended workflow.

**Feature 1 (Due dates + overdue filter):**
- `app/models.py`: added `due_date: Optional[date]` to all three task models, plus a
  `field_validator("due_date", mode="before")` rejecting non-`str`/non-`None` input. This closed a
  real gap found during review: Pydantic's native `date` type silently accepts an int/float as a
  Unix timestamp instead of returning 422, which would have made the "any other format returns
  422" acceptance criterion false for numeric input specifically.
- `app/storage.py`: `add_task` persists `due_date`; a new `is_overdue()` helper (due date in the
  past, status not `Done`); `get_all_tasks` gained an `overdue` filter. `update_task` needed no
  changes — verified (not assumed) that its existing `exclude_unset` + `model_copy` pattern
  already handles omit-vs-null correctly, the same way it already did for `assignee`.
- `app/main.py`: exposed `overdue` as a query parameter on `GET /tasks`.
- Tests: 14 new tests (creation, update, and the overdue filter, including the Done-status
  exclusion and the numeric-input rejection).
- Frontend: due-date input in the modal, `.task-due-date` display on cards, `isOverdue()`/
  `todayIsoString()` (naive local date, no UTC) driving an `overdue` CSS class, and a "Show
  overdue only" toggle wired into `fetchTasks`.
- Break Tests: 2 (title+transition atomicity reused from earlier in the session; `is_overdue()`'s
  `Done`-exclusion clause).

**Feature 2 (Tags / labels):**
- Before implementing storage, a review of the original feature brief against the drafted user
  stories surfaced two gaps: "filter by tag" and "update tags" were listed in the brief's "Good
  tests to include" column but had never become explicit acceptance criteria. Added **Story 7**
  (filter tasks by tag) and **Story 8** (update a task's tags, replacing not merging) to
  `user-stories.md` *before* writing the corresponding code, rather than building undocumented
  backend behavior.
- `app/models.py`: added `tags: list[str]` (required, defaulting to `[]`) to `TaskCreate`/
  `TaskResponse` and `Optional[list[str]]` to `TaskUpdate`; a `tags` validator trims each value,
  rejects blank entries, and deduplicates case-insensitively while preserving first-occurrence
  casing/order.
- `app/storage.py`: `add_task` persists `tags`; `get_all_tasks` gained a case-insensitive `tag`
  filter combining with `status`/`priority`/`overdue` via AND logic. `update_task` was verified
  (not assumed) against all three Story 6/8 cases: omit leaves unchanged, explicit `[]` clears,
  explicit new set replaces without touching other fields.
- `app/main.py`: exposed `tag` as a query parameter on `GET /tasks`.
- Tests: 13 new tests (creation, update — including the replace-vs-merge case — and the tag
  filter, including its AND-logic combination with `status`).
- Frontend: comma-separated tags input in the modal (locked-in simplest option over an
  interactive chip widget), `.tag-chip` rendering on cards, and a tag-filter text input;
  `fetchTasks` was rewritten to build its query with `URLSearchParams` so the `overdue` and `tag`
  filters can combine, instead of the single-condition ternary it had before.
- Break Tests: 2 (Story 8's replace-not-merge behavior; the tag filter's AND-logic combination
  with other filters — both isolated to fail exactly one targeted test, verifying the rest of the
  suite was unaffected).

**Net result:** both features fully implemented end-to-end (backend, tests, frontend), 45 pytest
tests passing (18 baseline + 27 new), 4 Break Tests documented, no new dependencies introduced.
