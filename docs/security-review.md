# Security Review — Task Tracker

## Executive summary

Read-only security audit of the Task Tracker repo, combining an AI pass with an
independent manual scan. **No critical or high-severity issues.** The backend
enforces strict enum/type validation, and the frontend is **XSS-clean** — every
task field is rendered via `textContent`, never `innerHTML`. The absence of
authentication is an **intentional, documented** decision for this local,
single-user course project (A-1), not a defect at this scope.

The most material items are a validation inconsistency (V-1 — some free-text
fields are uncapped while `title` is capped) and two **You-only** findings the
automated pass missed (M-1, M-2). Both You-only findings are the same root
pattern — **enforcement asymmetry**, where a rule is applied on one path and
skipped on another — which is the headline learning from this review: the AI
pass covered validation and build/CI hygiene well but did not surface either
asymmetry; the manual trace did.

**At a glance:**

| Disposition | Findings |
|-------------|----------|
| Critical / High | *(none)* |
| Valid — hardening / validation (Low) | V-1, D-1, D-2, CI-1, M-1, M-2 |
| Valid — documented scope boundary | A-1, C-1 (E-1 as Info) |
| Noise (true but not actionable at this scope) | hardcoded HTTP URL, missing CSP |
| Reconciliation | AI + manual **agree** on the shared set; **You-only:** M-1, M-2; **AI-only:** none |

Severities are relative to the project's stated **local, single-user,
no-deployment** scope; several items (A-1, C-1, the HTTP URL) rise only if the
app is ever exposed beyond localhost.

---

Read-only security audit of the Task Tracker repository. Findings are separated
into two sections so a reader does not mistake the project's **intentional,
documented scope decisions** for unaddressed holes:

1. **Scope-boundary decisions** — documented choices for a local, single-user
   course project. Listed for completeness, not defects to fix at this scope.
2. **Hardening / validation gaps** — genuine items worth addressing regardless
   of scope (validation consistency and build/CI hygiene).

Scope context: Task Tracker is a **local, single-user** course project with an
in-memory store, **no authentication, and no deployment** — data is lost when
the server stops (`AGENTS.md:8-12`, `CLAUDE.md §7`). Severities are relative to
that scope; several items rise in severity only if the app is ever exposed
beyond localhost.

---

## Section 1 — Scope-boundary decisions (documented, not defects)

| ID | Severity | File / location | Finding | Evidence | Notes / next step | Confidence |
|----|----------|-----------------|---------|----------|-------------------|------------|
| A-1 | Info (by design) | `app/main.py` (all routes) | **No authentication/authorization.** Any client can create/read/update/delete every task. Explicitly documented as intentional for a local, single-user project. | No auth dependency on any route; `AGENTS.md:126-127`, `CLAUDE.md §7`. | None required at this scope. If ever exposed beyond localhost, add authn/authz before exposure. | High |
| C-1 | Low / Info | `app/main.py:21` | **CORS allows the `"null"` origin.** Sent by `file://` pages and sandboxed iframes; lets any local file/sandboxed page call the API. Deliberate, to support the `file://`-served frontend. Impact bounded: `allow_credentials` defaults to False and there is no auth/cookies. | `allow_origins=[..., "null"]` (`app/main.py:18-22`); origin list documented in `CLAUDE.md §6`. | Keep for local file-served frontend; drop `"null"` if the app is ever deployed. | High |
| E-1 | Info / Low | `app/main.py:132,169,174,198` | **404 detail echoes the raw `task_id`.** Reflects attacker-controlled input, but low risk: JSON response, and the frontend renders all task fields via `textContent`, not `innerHTML`. | `detail=f"Task with id {task_id} not found"`; frontend uses `textContent` (`frontend/index.html:563,570,577,587,599,604`). | Optional hardening: return a generic "task not found" without echoing input. | High |

---

## Section 2 — Hardening / validation gaps

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|----|----------|-----------------|---------|----------|---------------------|------------|
| V-1 | Medium | `app/models.py:24,27,29` (and `:67,70,72`) | **Inconsistent input validation — unbounded fields.** Only `title` is length-capped (200). `description`, `assignee`, each tag value, and the `tags` list itself have no max length or count. With the unbounded in-memory store, large/many payloads grow memory. | `title` capped at `app/models.py:37-38`; `description` (`:24`), `assignee` (`:27`), tags (`:48-60`) uncapped. Store is an unbounded dict (`app/storage.py:7,35`). No request-body size limit. | Add `max_length` to `description`, `assignee`, per-tag, and a max `tags` count; consider a body-size limit. *(DoS impact only relevant if exposed; the validation inconsistency stands regardless.)* | High |
| D-1 | Low | `requirements.txt:1-6` | **Dependencies unpinned, no upper bound, no lockfile/hashes.** All deps use `>=` only → non-reproducible builds; exposed to a breaking/compromised upstream release. | `fastapi>=0.110`, `uvicorn[standard]>=0.29`, `pydantic>=2.6`, etc. No `pyproject.toml`/lock. | Pin exact versions (or a hash-locked constraints file) for CI and Docker reproducibility. | High |
| D-2 | Low | `Dockerfile:2,12` | **Base image pinned only by mutable tag** `python:3.11-slim` (not by digest). | `FROM python:3.11-slim AS builder` / `FROM python:3.11-slim`. Non-root `USER app` and `--no-cache-dir` are already good practice. | Pin the base image by `@sha256:` digest. | High |
| CI-1 | Low | `.github/workflows/ci.yml:3-5` | **No `permissions:` block; triggers on all branches.** Inherits repo-default `GITHUB_TOKEN` permissions instead of least-privilege. | `on: push / pull_request` with no branch filter; no `permissions:` key; `pip install -r requirements.txt` (`:19-22`). | Add `permissions: contents: read` at the workflow level; consider pinning deps (ties to D-1). | Medium |

---

## Section 3 — Manual scan finding (You-only)

Found during an independent manual trace of `app/business_rules.py`, **not**
surfaced as a finding by the AI security pass (reconciliation: **You-only**).

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|----|----------|-----------------|---------|----------|---------------------|------------|
| M-1 | Valid — Low | `app/main.py:51-59` (create) vs `:166-170` (patch); model default `app/models.py:25` | **Status-transition rule enforced on PATCH but bypassed on create.** `validate_status_transition` runs only on `PATCH`; `POST /tasks` accepts any `status` (default `ToDo`, but `Done`/`InProgress` are equally accepted), so a task can reach `Done` without a valid transition. Benign here — the rule is workflow-only and the bypass is documented — but "validate-on-edit-not-create" is a serious bug class when the enforced rule is security-relevant. | Rule called only at `app/main.py:166-170`; create path `app/main.py:51-59` performs no transition check; `TaskCreate.status` default `app/models.py:25`; documented as intentional `AGENTS.md:70-71`. | Documentation note (already documented as intentional). Optional backlog: decide whether create should also be constrained. | High |
| M-2 | Valid — Low | backend `app/models.py:48-60`; frontend `frontend/index.html:770` (split) & `:718` (join) | **Comma-in-tag rule enforced only client-side.** The UI splits tag input on commas, so a tag can never contain one; the backend tag validator does no comma check, so `POST /tasks {"tags":["urgent,backend"]}` stores a single comma-bearing tag. Opening that task in the edit modal then join-splits it, silently turning one tag into two — data corruption with no error. Same asymmetry class as M-1 (rule enforced on one path only), here client-side-only validation. | Backend validator only trims/blank-checks/de-dupes (`app/models.py:48-60`); UI `split(',')` (`frontend/index.html:770`) and `join(', ')` (`:718`); documented `AGENTS.md:90-94`. | Backlog: reject or escape commas in the tag validator, or stop relying on comma join/split in the UI. | High |

**Reconciliation note:** the AI/manual reconciliation is no longer
all-Agreement — the AI pass produced the shared set (A-1, C-1, E-1, V-1, D-1,
D-2, CI-1); the manual pass added **M-1** and **M-2** as **You-only** findings,
neither surfaced by the AI security pass. No **AI-only** findings (every AI item
was reviewed manually). Both You-only findings are instances of the same
enforcement-asymmetry class — a rule applied on one path and skipped on another.

### Context behind each You-only finding

Each manual finding is run through three questions — *what business logic, scope
decision, or threat-model context explains it?* — to pin down why it exists and
the precise condition under which it would escalate from benign to security-relevant.

**M-1 — transition rule bypassed on create**

- **Business logic:** the transition graph (`ToDo→InProgress→Done`,
  `Done→InProgress`) models a Kanban workflow. Create-in-any-status is
  deliberate so already-in-progress or already-done work can be seeded/backfilled
  without walking it through each state.
- **Scope decision:** documented as intentional (`AGENTS.md:70-71`) — creation is
  explicitly exempt from the transition rule.
- **Threat model:** none today. Status is a **UX invariant, not a security
  control** — no privilege, immutability, or side-effect is gated on it, and the
  app is local/single-user/no-auth. It becomes a real **state-machine bypass**
  only if a status ever gates something security-relevant (e.g. `Done` implies
  immutability, an approval, or a triggered action), at which point
  create-in-that-status sidesteps the gate.

**M-2 — comma-in-tag rule enforced only client-side**

- **Business logic:** "no comma inside a tag" is **not a domain rule** — it is an
  artifact of the UI choosing comma as its multi-tag delimiter
  (`split(',')` / `join(', ')`). The backend treats tags as opaque strings, so it
  has no reason to reject commas.
- **Scope decision:** documented frontend-only behavior (`AGENTS.md:90-94`); the
  API deliberately accepts any non-blank tag string.
- **Threat model:** no injection path — tags render via `textContent`. The
  concrete risk is **self-inflicted data corruption**: an API-created comma-tag
  splits into two on edit-save. It escalates only if some consumer parses tags as
  a comma-delimited structure (CSV export, a `tag,tag` query), where a
  comma-bearing tag could break parsing or forge extra tags.

### Considered and graded Noise

Examined during the manual scan and **deliberately not actioned** — recorded so
the review shows what was looked at and consciously dropped, not overlooked.

| Candidate | Evidence | Grade | Reasoning |
|-----------|----------|-------|-----------|
| Hardcoded plain-HTTP API base URL | `frontend/index.html:446` (`const API_BASE_URL = 'http://localhost:8000'`) | Noise (scope) | Correct for a local single-user course app. Only two latent issues *if deployed*: hardcoded `localhost` breaks a real deployment, and plain `http` gives no transport encryption. Same scope-boundary flavor as A-1/C-1; would become Valid-Low once deployment is in scope. |
| No Content-Security-Policy / security headers | No CSP in HTML `<head>`; page served via `python -m http.server` (`AGENTS.md:34-40`) | Noise (defense-in-depth, N/A here) | CSP mitigates XSS, but the frontend has no XSS sink — every field is rendered via `textContent` (verified: `frontend/index.html:563,570,577,587,599,604`; only `innerHTML` use clears the list at `:502`). Defense-in-depth on a hole that does not exist. |

Also examined and **out of scope** (robustness/UX, not security): silent load
failure with no user-facing error (`frontend/index.html:494-496`); no debounce
on the tag filter (`frontend/index.html:746`).

---

## Files inspected

- `app/main.py` (routes, CORS, error handling)
- `app/models.py` (Pydantic validation, enums)
- `app/storage.py` (in-memory store)
- `app/business_rules.py` (status-transition rule)
- `tests/test_tasks.py` (expected behavior)
- `requirements.txt`, `.env.example`, `.gitignore` (partial)
- `Dockerfile`
- `.github/workflows/ci.yml`
- `frontend/index.html` (rendering / fetch paths, grep-targeted around lines 446–830)
- `AGENTS.md`, `CLAUDE.md`

## Categories where no issue was found

- **Enum / type handling:** `TaskStatus`/`TaskPriority` are strict enums; invalid
  values → 422. `due_date` has an explicit type guard (`app/models.py:41-46`).
  `extra="forbid"` rejects unknown fields (`app/models.py:21,64,111`).
- **Broad exception behavior:** No bare `except:` / `except Exception` swallowing
  in `app/`. Errors are explicit `HTTPException(404/422)`.
- **Stack traces / verbose errors:** No custom handler leaks internals; responses
  are clean status codes. `--reload` (debug) appears only in the local run
  command, not in the Docker `CMD` (`Dockerfile:27`).
- **Secrets / unsafe config:** No secrets committed. `.env.example` holds only
  non-secret placeholders (`PORT`, `APP_ENV`). Verified first-hand this review
  that the app reads no environment/config: `grep -rnE
  "dotenv|load_dotenv|os\.environ|getenv" app/` returns no matches. Dockerfile
  copies only `app/` (no tests, no `.env`) and runs as non-root (`Dockerfile:14,19,23`).
- **Frontend XSS:** All task-derived content is rendered with `textContent`,
  never `innerHTML` (the only `innerHTML` use clears the list,
  `frontend/index.html:502`). No injection sink found.

## Assumptions & limits

- **Read-only review.** The app, tests, and `pip install` were not run; no
  network/advisory scan was performed. D-1/D-2 are configuration/reproducibility
  risks, not confirmed CVEs.
- The frontend was reviewed via targeted search plus the relevant JS regions
  (fetch/render paths), not a full line-by-line read of all 831 lines.
- Severities are relative to the project's stated **local, single-user,
  no-deployment** scope. A-1 and C-1 rise in severity only if the app is exposed
  beyond localhost.
- Per the Module 5 guardrails (`AGENTS.md:96-114`), this was analysis only — no
  application code was modified.
