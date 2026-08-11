# Architecture Docs — Strategy A vs. B Comparison

Reflection on producing the same one-page architecture doc two ways:
**Strategy A** (minimal context — a one-line task description, inspect files as
needed) vs. **Strategy B** (structured context — `AGENTS.md` + file summaries).
Compares `docs/architecture-A.md` and `docs/architecture-B.md`.

## What became more specific in B

Almost every gain traces to AGENTS.md §3 handing over rules ready-made:

| Detail | Strategy A | Strategy B |
|---|---|---|
| Creation bypasses the transition rule | absent | **stated** (§3) — a non-obvious, high-value rule |
| Exact transitions + same-status/`Done→ToDo` → 422 | generic "invalid → 422" | **spelled out** (§5) |
| Overdue formula (`due_date` < today local, status ≠ Done) | absent | **stated** (§5) |
| Filtering semantics (AND-combined, tag case-insensitive) | absent | **stated** (§5) |
| Tag-comma quirk (frontend-only, not backend-enforced) | absent | **stated** (§5) |
| Endpoint list / `updated_at` refreshed on update | partial | **explicit** (§1, §2) |

The real dividend: B is meaningfully sharper on **business rules**, and got there
without file-spelunking because the structured context pre-digested them.

## What became too long

- **§5 is overstuffed** — six clusters (validation, storage, transitions, errors, overdue/filtering, CORS/tags). For a one-page *architecture* doc, that pushes past the limit.
- **Feature-behavior creep** — overdue formula, filtering semantics, and the tag-comma quirk are behavioral details, not architecture; they pad the overview. A stayed leaner by omitting them.
- **Citation noise** — repeated "(AGENTS.md §3)" tags add provenance but weight.

Net: B traded A's one-page discipline for completeness.

## What became too confident

- **B's confidence is borrowed from a summary, not verified against code.** Every asserted rule rests on AGENTS.md §3, a **secondary source**. A attributed what it *inspected* and hedged. If AGENTS.md were stale relative to `app/`, B would be **confidently wrong** with no signal that it hadn't been checked against code.
- **Scope over-reach** — stating overdue/tag-comma behavior in an *architecture* doc gives feature rules the same authority as structural facts.
- **Fair caveat** — in this case B is not actually wrong: those exact rules were cross-checked against the code during the security review (`docs/security-review.md`), so AGENTS.md is accurate here. But that verification happened *outside* the Strategy-B method; the doc itself gives a reader no signal that the rules were checked against code rather than copied from a summary.

## Net takeaway

Structured context (B) buys **specificity cheaply** but tempts two failure modes:
**over-including** (length) and **over-trusting the summary** (unearned
confidence). Minimal context (A) stayed lean and honest about its evidence base
but was **vaguer on the rules** and needed file inspection to say anything precise.

**Ideal doc = B's rule-specificity + A's "here's what I actually verified"
hedging + a one-page cut** that pushes overdue/filtering/tag-comma into a separate
feature doc.
