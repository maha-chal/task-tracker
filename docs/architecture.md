# Architecture Doc — Context-Strategy Comparison Log

The same one-page architecture-document task was run three ways, to compare how
much the *context strategy* changes the output. This log compares the three
drafts and records the choice for the final architecture doc.

- **Strategy A — minimal context:** a one-line task description; inspect files as needed. → `docs/architecture-A.md`
- **Strategy B — structured context:** `AGENTS.md` + file summaries. → `docs/architecture-B.md`
- **Strategy C — targeted context:** only `app/main.py`, `app/models.py`, `app/storage.py`. → `docs/architecture-C.md`

None of the three invented repo facts; the differences are what each **omitted**
or how it **framed** its claims.

## 1. Strategy comparison

| Strategy | What it got right | What it got wrong / missed / invented | Best-suited task shape |
|---|---|---|---|
| **A — minimal context** | Full product picture in §1 (Kanban board, drag-drop, create/edit modal, overdue highlighting, tag filtering); complete 10-file key-files list; create flow end-to-end *including the frontend re-fetch*; specifics like CORS `"null"`, hardcoded `localhost:8000`, `textContent` rendering. | **Invented:** none. **Missed:** left the business rules vague — "invalid → 422" with **no** specific transitions, no overdue formula, no tag-comma quirk. **Framing:** carries generic FastAPI sentences (validation→422, `response_model`→201) that describe *any* FastAPI app. | Fast, broad orientation when you can inspect freely — a readable first-pass or beginner-facing overview. |
| **B — structured context** | Most repo-specific on rules: exact transitions (`ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`), the creation-bypass, overdue formula, filtering (AND / case-insensitive), tag-comma quirk, CORS, endpoint list. | **Invented:** none. **Framing:** confidence is *borrowed from AGENTS.md* (a summary), not verified against code. **Length:** §5 overstuffed, pushes past one page; feature-behavior creep + repeated citation noise. | Thorough reference/onboarding docs where precise rules matter and a trusted structured context (AGENTS.md) already exists. |
| **C — targeted context** | Accurate backend mechanics (data model, create flow, storage internals, validation, 404/422 handling, CORS config); scrupulously honest — marks everything outside the 3 files "not visible from the files I read." | **Invented:** none, by design. **Missed:** the actual transitions (`business_rules.py` unread), all frontend/product context, run/test/CI/Docker, scope framing; §4 lists **fewer than five** files. | Focused subsystem work (backend internals) or high-stakes changes where zero invention and full verifiability beat breadth. |

## 2. Verdict

**Chosen: Strategy B as the base for the final architecture doc — validated and
trimmed.** B is the only draft that captured the *specific* rules a reader
actually needs (the exact transitions, the creation-bypass, the overdue formula,
the tag-comma quirk); A left those vague and C couldn't see them at all. B's two
weaknesses are fixable without changing strategy: its length (move
overdue/filtering/tag-comma into a feature section to stay one page) and its
borrowed confidence (its rules were independently cross-checked against the code
during the security review, so the final doc can state them as *verified*, not
*summarized*). Keep A's product framing in §1 (the board/UI context B
under-emphasized) and C's discipline of attributing any claim that came from
inspection rather than the structured context. Net: **B for specificity,
corrected with A's product framing and C's honesty about sourcing.**

## 3. Context-engineering rule

> **For writing a one-page architecture or onboarding doc for the Task Tracker
> (the Strategy A/B/C exercise), I use structured context (Strategy B) grounded in
> AGENTS.md, because it surfaces the specific business rules — exact transitions,
> overdue logic, the tag-comma quirk — that the minimal-context draft left vague.**
> **For a bounded, must-be-exact read of one module — the line-by-line walkthrough
> of the CRUD endpoints in `app/main.py`, or any single security-review finding I
> have to state precisely — I use targeted context (Strategy C) anchored on that
> file plus the files it imports, because reading only those keeps every claim
> verifiable and blocks the borrowed confidence that AGENTS.md-based context
> invites.**
