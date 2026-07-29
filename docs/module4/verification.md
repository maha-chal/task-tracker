# Module 4 — Verified Interactions Summary

Scope: direct verification of API claims from `app/main.py`, `app/models.py`, and
`app/business_rules.py`, following the "verify, don't assume" principle established in
`CLAUDE.md`. Five claims checked — one from source code, four from live requests against the
running backend.

## 1. Status-transition rule content

- **Method:** source read, `app/business_rules.py` (lines 5-18).
- **Result:** `VALID_TRANSITIONS` allows exactly `ToDo → InProgress`, `InProgress → Done`,
  `Done → InProgress`; everything else (including same-status and `Done → ToDo`) raises
  `HTTPException(422)`.

## 2. Blank title → 422

- **Method:** live `POST /tasks` with `{"title": "   "}`.
- **Result:** `422`, `"msg":"Value error, Title is required and cannot be blank"` — matches
  `app/models.py`'s `TaskCreate.validate_title`.

## 3. Malformed `due_date` → 422

- **Method:** live `POST /tasks` with `{"title": "Test", "due_date": "07/24/2026"}`.
- **Result:** `422`, `"type":"date_from_datetime_parsing"` — confirmed as Pydantic's native date
  parser rejecting the format, distinct from the custom type-guard validator
  (`validate_due_date_type`).

## 4. Blank tag → 422

- **Method:** live `POST /tasks` with `{"title": "Test", "tags": ["ok", "   "]}`.
- **Result:** `422`, `"msg":"Value error, Tag values cannot be blank"` — matches
  `app/models.py`'s `validate_tags`; confirmed the whole array is rejected as a unit, not
  partially applied.

## 5. Unknown field → 422

- **Method:** live `POST /tasks` with `{"title": "Test", "madeUpField": "value"}`.
- **Result:** `422`, `"type":"extra_forbidden"` — confirms `ConfigDict(extra="forbid")` is
  actually enforced at runtime, not just declared.

## Net outcome

All 5 claims held up exactly as documented — no discrepancies found between what the code claims
to do and what it actually does when exercised. One process issue was found and resolved along
the way (a stale server process silently occupying port 8000, causing every request to hang
instead of respond) — not a code defect, but worth noting as part of the verification trail.
