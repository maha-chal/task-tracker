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

*(To be completed after Feature 1 and Feature 2 are implemented and verified, per the
recommended workflow: backend → tests → frontend, verifying each layer before moving on.)*
