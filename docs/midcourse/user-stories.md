# User Stories — Mid-Course Project

Selected features: **Due dates + overdue filter** and **Tags / labels**.

User role used throughout: `team member`. No login, authentication, user accounts, admin roles,
notifications, mobile, or real-time updates are referenced, per scope.

## Feature 1: Due dates + overdue filter

### Story 1 — Set a due date on creation

As a team member, I want to set a due date when creating a task so that I know when it needs to
be finished.

**Acceptance Criteria**
- `due_date` is optional; omitting it still creates the task successfully.
- A provided `due_date` must match `YYYY-MM-DD` (ISO 8601 date, no time component); any other
  format returns HTTP 422.
- A created task's card renders a `<span class="task-due-date">` element showing the due date
  formatted as `YYYY-MM-DD`, verifiable via `document.querySelector('.task-due-date').textContent`.
- A due date may be any valid calendar date, including a date in the past — a task can be
  created already overdue.

**AI assumption corrected:** the original draft only checked "is this a valid date," with no
statement on whether past dates are allowed. Corrected to explicitly allow past due dates, since
disallowing them would block a realistic use case (logging work that's already late).

### Story 2 — Update a task's due date

As a team member, I want to update a task's due date so that I can adjust deadlines as work
changes.

**Acceptance Criteria**
- Sending a new `due_date` on update changes only that field; other fields remain unchanged.
- Omitting `due_date` from the update leaves the existing value unchanged; sending
  `due_date: null` explicitly clears it — these are not the same request.
- An invalid due date format on update (same `YYYY-MM-DD` format as task creation) returns
  HTTP 422 and the task's due date is left unchanged.

**AI assumption corrected:** the null-vs-omitted distinction for clearing `due_date` was applied
silently (by analogy with the existing `assignee` field) rather than stated. Corrected to make
this explicit in the acceptance criteria so it isn't lost during implementation.

### Story 3 — Mark and filter overdue tasks

As a team member, I want tasks past their due date to be visibly marked overdue so that I can
prioritize them.

**Acceptance Criteria**
- A task whose `due_date` is earlier than the current date renders with an `overdue` class on
  its card element (e.g., `<article class="task-card overdue">`), verifiable via
  `card.classList.contains('overdue')`.
- A task with `due_date: null` never has the `overdue` class applied to its card, regardless of
  the current date.
- A task with `status: "Done"` never has the `overdue` class applied to its card, even when
  `due_date` is earlier than the current date.
- `GET /tasks?overdue=true` returns only tasks whose `due_date` is earlier than the current date
  and whose `status` is not `Done`; `GET /tasks` without the parameter returns all tasks
  regardless of overdue state.

**AI assumption corrected:** the original draft applied "overdue" regardless of task status.
Corrected to exclude `Done` tasks — a completed task shouldn't be flagged overdue just because it
finished after its due date, since "overdue" should only describe incomplete work.

## Feature 2: Tags / labels

### Story 4 — Add tags to a task

As a team member, I want to add tags to a task so that I can categorize it for easier
organization.

**Acceptance Criteria**
- Tags are optional; a task can be created with zero, one, or multiple tags.
- Each tag value is trimmed of whitespace before being saved.
- Tags are submitted and returned as a JSON array of strings (not a comma-separated string), to
  keep the frontend's tag-chip rendering straightforward.
- A created task's card renders one `<span class="tag-chip">` element per tag, each containing
  the exact tag text, verifiable via `document.querySelectorAll('.tag-chip')`.

**AI assumption corrected:** the feature brief allowed tags as *either* a list or a normalized
comma-separated field, and the original draft picked "list" silently. Corrected to state this as
an explicit decision, since it changes the API request/response contract.

### Story 5 — Reject blank tags

As a team member, I want blank tags to be rejected so that the tag list stays meaningful.

**Acceptance Criteria**
- Submitting a tag that is empty or whitespace-only returns HTTP 422, and the task is not
  created or updated.
- Existing valid tags on the task are unaffected when a blank tag submission is rejected.
- *(Assumption, not in the original brief: duplicate tag values are deduplicated rather than
  rejected.)* Duplicate tag values (case-insensitive) are deduplicated before saving; submitting
  the same tag twice results in it being stored once.
- The 422 response body's `detail` field contains the exact substring `"tag"` (e.g., a message
  like `"Tag values cannot be blank"`), matching the existing pattern of asserting exact `detail`
  text used elsewhere in this project's tests.

**AI assumption corrected:** the original draft only addressed blank/whitespace tags and silently
allowed duplicate tag values. Corrected to require case-insensitive deduplication, since allowing
duplicates would let the same tag chip render twice on a card with no benefit.

### Story 6 — Preserve tags across an unrelated update

As a team member, I want a task's tags to remain unchanged when I update an unrelated field so
that I don't lose organization work by accident.

**Acceptance Criteria**
- Updating a task's title, description, priority, or assignee without including tags in the
  request leaves the existing tags unchanged.
- After the update, the task's card still renders exactly the same set of `.tag-chip` elements
  (same count, same text values) as before the update.
- Sending `tags: []` explicitly clears all tags from the task; omitting `tags` from the request
  body leaves existing tags untouched — these are distinct request shapes, not equivalent.

**AI assumption corrected:** the empty-array-vs-omitted-field distinction for `tags` was implicit
in the original draft. Corrected to state it explicitly, since this is easy to get backwards
during implementation and directly affects whether "clear all tags" and "no tag change" are
handled correctly.
