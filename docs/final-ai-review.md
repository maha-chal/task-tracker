# Final AI Review and Ownership Evidence

Main AI-assisted-coding evidence document for the final project. Branch:
`final-project`. Date: 2026-08-12 (UTC — the corresponding commits are stamped
2026-08-13 in local time, UTC+3).

## AGENTS.md guardrails

- **Repo-specific stack and commands included:** **yes** — `AGENTS.md` §2 records the
  stack (Python 3.11, FastAPI, Pydantic v2, Uvicorn, pytest, httpx), the run command
  (`uvicorn app.main:app --reload --port 8000`), the frontend command, the test command,
  and the Docker build/run commands.
- **Docs-first / read-first guardrail included:** **yes** — §4 requires read-only analysis
  first and writing only under `docs/` unless another path is explicitly approved, plus
  "cite files inspected" and "admit uncertainty" rules.
- **Unexpected `app/` / `frontend/` edits rule included:** **yes** — §4 states that `app/`
  and `frontend/` may be changed only for a small bug fix, a security fix, or a
  documentation-supported correction, and that any such change must be explained in this
  file. §4 was re-scoped during the final project so it covers this phase, not only
  Module 5.

**`app/` and `frontend/` changes made during the final project: none.** All final-project
edits were to `.github/workflows/ci.yml`, `README.md`, `AGENTS.md`, and `docs/`.

## AI code review mini-log

Diff reviewed: commit **`38600ae`** — "Add final-project release evidence, README section,
and CI test scope fix" (`.github/workflows/ci.yml`, `README.md`).

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| README's Docker block shows `docker run --rm -p 8000:8000 task-tracker` immediately followed by `curl .../health`, but without `-d` the run command occupies the terminal, so the `curl` cannot execute in the same shell. README §4 warns to use a second terminal for the local server; the Docker block did not. | **Useful** | A real documentation defect that would block the teammate the project is written for. README §4 already sets the "second terminal" precedent, so the omission is inconsistent. | Confirmed by running the container: `docker run` holds the foreground. **Fixed** — added an explicit second-terminal note before the `curl` step. |
| README's Final Project section shows only `.\venv\Scripts\Activate.ps1` (PowerShell), while README §3 documents cmd and macOS/Linux variants. A teammate on macOS or Linux following only this section hits a broken command. | **Useful** | The stated goal is that another developer can clone and run the repo; a Windows-only activation line defeats that for non-Windows users. | Cross-checked against README §3, which lists all three variants. **Fixed** — the Final Project section now lists PowerShell, cmd, and macOS/Linux activation. |
| Widening CI to `pytest tests/` changes future collection behaviour: anything later named `test_*.py` is collected automatically, so renaming `tests/verify_a.py` to `test_verify_a.py` would silently start running it in CI. | **Noise** | Speculative — it depends on a rename nobody has proposed. Current behaviour was verified, and auto-collecting genuine new test files is the desired outcome. | Verified that `pytest tests/` and `pytest tests/test_tasks.py` collect the **same 45 tests** today. No action. |
| `ci.yml` has no `permissions:` block, so the workflow inherits default `GITHUB_TOKEN` permissions instead of least privilege (`permissions: contents: read`). | **Noise** | Same item as security finding CI-1, already graded Noise: this workflow only checks out code and runs tests — no deploy, no secrets, minimal blast radius. | Consistent with the CI-1 grade in `docs/security-review.md`. No action. |
| The commit mixes three concerns — a CI configuration change, README documentation corrections, and a new evidence document — and could be split for reviewability. | **Noise** | The three are causally linked: widening CI is what made the README claims false, and the evidence document records both. Splitting would obscure that chain. | Rationale recorded in the commit message. No action. |

Two of the five comments identified real defects in text written minutes earlier; both were
fixed. Three were rejected as not actionable.

## AI security mini-review

Source: `docs/security-review.md` (read-only audit; no application code was modified).
Grades below are mine, and in three cases they differ from the AI's proposed severity.

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| **A-1** — no authentication on any route | `app/main.py` (all routes); documented `AGENTS.md` §1, §5 | **Valid** (documented scope limitation) | Real and would matter outside a classroom, but intentional and documented for a local, single-user app. Not a defect at this scope. | Backlog gate: add authn/authz before any non-localhost deployment. |
| **V-1** — `description`, `assignee` and `tags` have no length or count limits while `title` is capped at 200 | `app/models.py:24,27,37-38,48-60`; unbounded store `app/storage.py:7,35` | **Valid (Low)** | A genuine inconsistency inside the validation layer, independent of deployment. DoS impact is only relevant if exposed. | Backlog: add `max_length` to the free-text fields and a cap on tag count. |
| **D-2** — Docker base image pinned by mutable tag `python:3.11-slim`, not by digest | `Dockerfile:2,12` | **Valid (Low)** | Reproducibility/supply-chain hygiene: the tag can move under the same name. | Backlog: pin `FROM python:3.11-slim@sha256:<digest>`. |
| **C-1** — CORS allows the `"null"` origin | `app/main.py:18-24` (no `allow_credentials`) | **Noise** | Impact needs two future conditions at once — deployment beyond localhost *and* credentials being enabled. Nothing sensitive is CORS-protected today. | None. Revisit only if deployed. |
| **D-1** — dependencies unpinned (`>=`, no lockfile) | `requirements.txt:1-6` | **Noise** | Hygiene rather than a vulnerability, and CI installs successfully today. Downgraded from the AI's "Valid (Low)". | None at this scope. |
| **CI-1** — no `permissions:` block in the workflow | `.github/workflows/ci.yml:3-5` | **Noise** | The workflow only checks out code and runs tests — no deploy step, no secrets used. Blast radius is minimal. | None. |
| **E-1** — 404 responses echo the raw `task_id` back to the client | `app/main.py:132,169,174,198`; frontend renders via `textContent` (`frontend/index.html:563-604`) | **Noise** | Technically true but with no exploit path: JSON response, no HTML sink, no authorization boundary to leak across. | None. |

## Manual security check

Beyond reviewing the AI's findings, I traced `app/business_rules.py` myself, following the
inputs rather than reading the AI's conclusions.

Working through where `validate_status_transition` is actually *called*, I found that the
rule is enforced on `PATCH /tasks/{id}` (`app/main.py:166-170`) but **not on task
creation** — `POST /tasks` accepts any `status` value, so a task can be created directly
in `Done` without ever passing through a valid transition (`app/main.py:51-59`;
`app/models.py:25`). This is recorded as **M-1** in `docs/security-review.md`.

Why it matters: the vulnerability class here is *enforcement asymmetry* — a rule applied
on one code path and silently skipped on another. In this repo the impact is low, because
status is a workflow convenience rather than a security control, and the bypass is
documented as intentional (`AGENTS.md` §3). But "validated on edit, not on create" is a
serious bug pattern whenever the rule being enforced actually gates something — an
approval, immutability, or a triggered side effect. Finding it required looking at the
*call sites*, not the function: `validate_status_transition` itself is correct.

For accuracy, a second finding (**M-2**, the comma-in-tag rule enforced only in the
frontend) also came out of this scan, but through guided analysis rather than
independently — my first reading of that behaviour was wrong and was corrected during
review. `docs/security-review.md` records that distinction rather than claiming both as
independent work.

## One AI output I rejected or corrected

The AI graded three security findings as **Valid (Low)** and proposed backlog actions for
each: **C-1** (CORS allows the `"null"` origin), **D-1** (unpinned dependencies), and
**CI-1** (no `permissions:` block in the CI workflow).

I did not accept those grades. Reviewing each against this project's actual scope — local,
single-user, in-memory, not deployed — I concluded that none is actionable here: C-1 needs
two future conditions to matter at all, D-1 is build hygiene with a passing install today,
and CI-1 protects a workflow that has no deploy step and uses no secrets. I **downgraded
all three to Noise**, and the AI's own review had flagged C-1 and CI-1 as borderline, which
supported the call.

What I did instead: I kept the findings documented with their evidence and my reasons, so
the decision is auditable rather than silent, and I made sure the grades stayed consistent
across documents — the CI-1 comment in the code review log above is graded Noise for the
same reason, rather than contradicting the security review.

## Three AI usage rules

Full versions with evidence in [`docs/ai-usage.md`](ai-usage.md) and
[`docs/ai-playbook.md`](ai-playbook.md).

1. **Never paste:** real external data (I substitute a synthetic fixture of the same
   shape); any file containing env vars, registry credentials, deploy targets or
   `secrets.*` references; or a raw stack trace — I send only the exception type, message
   and the single relevant frame, with absolute paths and usernames stripped.
2. **Always verify:** before committing any AI-generated artifact I mark it Yes / Partial /
   No for "can I explain this line by line?", and I commit only the **Yes** items. For
   Partial or No, I re-read the specific lines named in my action and re-mark before
   committing.
3. **Record AI contributions by:** adding a row to the "What I received from AI" table in
   [`docs/governance-worksheet.md`](governance-worksheet.md) — the artifact, the module, my
   line-by-line understanding, and a concrete follow-up action.

## Ownership statement

I am comfortable submitting this repository as my own work. I can explain the parts that
matter without assistance: the status-transition rule and why creating a task bypasses it,
why CI was widened from a single test file to the whole `tests/` directory, and what the
Docker non-root check proves about the image. The judgment calls here are mine — I
identified the create-path transition bypass (M-1) myself while tracing
`app/business_rules.py`, I downgraded three AI-graded security findings to Noise after
weighing them against this project's local, single-user scope, and I graded five AI review
comments on a real diff, accepting two as Useful and rejecting three as Noise. I checked
the CI evidence directly on GitHub Actions and confirmed both runs were green on the
`final-project` branch. Where AI drafted documentation or configuration, I reviewed it
against the running app and the repo before accepting it, and I rejected the parts that did
not hold up.
