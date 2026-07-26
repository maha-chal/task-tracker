# Reflection — Mid-Course Project

I used Claude Code for the entire workflow this module: drafting user stories, writing the
mini-ADR, generating each backend/frontend change from scoped prompts, writing pytest tests,
running Break Tests, managing git (branch, commits), and producing these docs. Everything went
through one tool rather than switching between a chat assistant and a separate coding agent,
which made it easy to keep context (decisions made earlier stayed visible when drafting later
prompts) but also meant I had to be the one enforcing scope discipline — nothing stopped the AI
from happily implementing more than I'd asked if I phrased a prompt loosely.

**Where it helped most:** catching a real correctness gap before it became a bug. When drafting
the `due_date` field, I assumed Pydantic's native date type would reject any malformed input with
422. Before accepting that as fact, I asked for it to be verified directly rather than taken on
faith — and it turned out Pydantic silently accepts an integer as a Unix timestamp instead of
rejecting it. That's the kind of framework-specific edge case I wouldn't have thought to test
manually, and catching it before writing the acceptance criterion (not after shipping it) meant
the fix was one small validator, not a debugging session later.

**Where it slowed things down:** environment friction, not logic. A recurring issue this session
was that servers started in the AI's own background tooling weren't reachable from its embedded
browser preview — a sandboxing quirk, not an application bug — which meant every frontend
verification needed a workaround (executing functions directly against the live page) instead of
a normal click-through test. It never blocked progress, but it added real back-and-forth
explaining why a "connection refused" wasn't a code problem.

**Where my review changed the result:** reviewing `user-stories.md` against the original feature
brief, after storage-layer work had already begun, surfaced that "filter by tag" and "update tags"
were both listed in the brief but had never become actual acceptance criteria. Rather than let the
AI quietly implement (or quietly skip) that gap, I asked whether it wasn't better to write the
missing stories first — which produced Stories 7 and 8, written and committed *before* the
corresponding code, so the backend behavior matches something documented rather than something
inferred after the fact.
