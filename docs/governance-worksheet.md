# Governance Retrospective — AI-Assisted Coding (Module 5)

A retrospective on what was shared with AI coding tools during this course, and
the data-handling risk of each. Companion to `docs/security-review.md`.

## Risk rubric

- **Low:** public code, course toy-project code, no sensitive data, no
  proprietary logic.
- **Medium:** private but non-sensitive code, internal implementation details, or
  non-public repo context with no secrets and no PII.
- **High:** credentials, tokens, secrets, production config, real customer/user
  data, regulated data, or code not authorized to share.

## What I shared with AI — risk classification

Classified per the rubric above; project size was **not** used to discount risk.

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Task Tracker code (M2–5) | **Low** | Course toy-project code — in-memory only, no secrets, PII, or proprietary logic. | Paste only the specific function/file the question needs rather than whole files; content itself is fine to share. | Confirm no `.env` values, API keys, or real config were ever embedded in a file that was pasted. |
| Test output and stack traces (M2–4) | **Medium** | Traces expose local absolute paths (including the OS username) and internal structure, even when the code is trivial — non-public environment detail. | Share only the exception type + message and the one relevant frame; redact absolute paths and usernames. | Whether any trace included environment variables, connection strings, or tokens (some frameworks dump these into traces). |
| Frontend code (M3) | **Low** | Single-file vanilla HTML/JS toy client; the only URL is a hardcoded `localhost`, no secrets or PII. | Fine as-is; if unsure, strip URLs/keys and paste just the relevant handler. | Confirm no real API endpoint, auth token, or API key was ever hardcoded in the JS (frontends are a common accidental-key location). |
| Dockerfile and CI YAML (M4) | **Low** *(for these files)* — but the highest-leakage category | These specific files hold no secrets: the Dockerfile only pip-installs as non-root; CI only checks out and runs pytest with the default token. | Before sharing infra files, scrub env vars, registry creds, deploy targets, and any `secrets.*` references; share a redacted copy. | Verify the shared versions matched these clean files and never referenced secrets, environments, or private deploy config — if they had, this row would be **High**. |
| Any real external data used by mistake | **High** *(treat as High until identified)* | By its own description this may be real external data — which can contain PII, credentials, regulated, or unauthorized content, the exact High-risk categories. | Never paste real data into a prompt; use synthetic/mock fixtures that copy only the *shape* of the data. | **Needs clarification:** what was the data, did it contain PII/secrets/credentials, whose was it, and was sharing it authorized? |

### Notes on the classifications

- **"Any real external data" is the row that matters most** — marked High rather
  than guessed away. The safe default is High until the data is identified; the
  grade may drop once its contents are confirmed.
- **The Dockerfile/CI "Low" is conditional** — Low *because those files were read
  and are clean*, not because infra files are inherently safe. That category is
  where secrets most often leak, so the caveat stands.

## What I received from AI

Each AI-generated artifact and whether it was understood line-by-line before use.
The "Understood?" column is a self-report; where the honest answer is "No" or
"Partial," the Action names the exact lines to re-read before relying on it.

| Generated thing | Module | Understood line by line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | Yes — reviewed in depth during the security audit (enum handling; `title` capped vs. uncapped siblings = V-1). | Close **V-1**: add `max_length` to `description`/`assignee`/tags in `app/models.py`. |
| Frontend board and drag-and-drop logic | 3 | Partial — traced rendering (`textContent`) and tag logic (M-2), but not the optimistic drag update/revert path. | Re-read `frontend/index.html:638-676` (`handleDrop` optimistic update + revert-on-error) before trusting it, then mark Yes. |
| CI workflow | 4 | Yes — short file, reviewed (CI-1). | Close **CI-1**: add `permissions: contents: read` to `.github/workflows/ci.yml`. |
| Dockerfile | 4 | Yes — reviewed multi-stage build + non-root; discussed D-2. | Close **D-2**: pin the base image by digest in `Dockerfile`. |
| Security findings and plans | 5 | Yes — actively graded, reconciled, and found M-1/M-2 during independent manual review. | None — submit. Output was challenged, not accepted as-is. |

## Habits to change (in order)

Only two shared items cleared the Low bar. Sorted by **worst-case severity and
reversibility first** (standard data-governance priority), not by frequency.

| Order | Item (Risk) | Habit to change | Why this order | First concrete action |
|---|---|---|---|---|
| **1st** | Real external data used by mistake (**High**) | "No real data in a prompt — ever. Use synthetic fixtures." | Rare but catastrophic and irreversible — one slip can expose PII/secrets/regulated data and cannot be un-shared. Low frequency doesn't help; the tail risk does the damage. Also the easiest habit to adopt: a single bright-line rule, no judgment call. | Before any paste, ask "is this data real?" If yes → stop and mock it. Keep a small synthetic fixture ready to substitute. |
| **2nd** | Test output and stack traces (**Medium**) | "Redact before paste: exception type + message + the one relevant frame; strip absolute paths/usernames." | Frequent but low-severity — each leak is local paths, username, internal structure. Ranks second on severity, but note it fires far more often, so it is where the redaction reflex is actually built. | Copy the trace, delete the file-path prefixes and frames above the relevant one, then paste. |

**Principle:** fix the *irreversible catastrophic* habit first (even though rarer),
then the *daily-recurring* one. Rule #1 guards the outcome you can't undo; Rule #2
builds the everyday muscle. (If the rubric weights *frequency* over severity, the
order flips — stack traces would move to 1st.)

## Key takeaways

- **Redaction beats trust:** the two elevated rows (stack traces, real external
  data) are both about *incidental* content — paths, usernames, or data pasted
  without meaning to. Scrub before sharing, don't rely on the code being "just a
  toy."
- **Infra files need a pre-share scrub habit:** Dockerfiles and CI YAML were clean
  here, but they are the highest-probability place for an accidental secret.
- **Prefer minimal, synthetic snippets** over whole files or real data — smaller
  surface, lower risk, same answer quality.
