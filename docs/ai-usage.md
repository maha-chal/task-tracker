# My AI Usage Rules

Three personal rules for using AI coding tools, derived only from my Module 5
governance notes in `docs/governance-worksheet.md`. Each rule includes a
*teammate test* — a concrete way to tell whether a future action violated it.

## Rule 1 — What I will never paste

Before pasting into an AI tool I will **not** send:

- **(a)** real external data — I substitute a synthetic fixture of the same shape;
- **(b)** any file containing env vars, registry credentials, deploy targets, or
  `secrets.*` references — removed first;
- **(c)** a raw stack trace — I paste only the exception type, message, and the
  single relevant frame, with absolute paths and usernames stripped.

**Teammate test:** a violation is visible if the prompt contains real values,
secret references, or a `C:\Users\...`-style path/username.

*Source:* "Any real external data" (High) + Habit #1; Dockerfile/CI scrub list;
stack-traces row + Habit #2.

*Missing – add course evidence:* no pre-paste checklist/tool is defined to
confirm a snippet was scrubbed before sending.

## Rule 2 — What I will always verify before accepting

Before committing any AI-generated artifact I mark it **Yes / Partial / No** for
"can I explain it line by line?" I commit **only Yes** items. For **Partial/No**,
I re-read the exact lines named in my action (e.g. drag-and-drop was Partial →
re-read `frontend/index.html:638-676`) and re-mark before committing.

**Teammate test:** pick any line of a committed AI artifact and ask me to explain
it — if I can't, the rule was broken.

*Source:* "What I received from AI" — line-by-line self-report; intro note that
Partial/No means re-read the named lines first.

*Missing – add course evidence:* the objective test that separates "Partial" from
"Yes" is not defined.

## Rule 3 — How I will record AI contributions

For every AI-generated artifact I use, I add a row to my "What I received from AI"
table in `docs/governance-worksheet.md` capturing: the artifact, the module, my
line-by-line understanding (Yes/Partial/No), and an action (a specific finding to
close or specific lines to re-read).

**Teammate test:** compare the committed AI-generated files against the table —
any committed artifact with no matching row violates the rule.

*Source:* the "What I received from AI" table structure and its finding-linked
actions.

*Missing – add course evidence:* the notes don't define **when** to record (at
generation / commit / end of module) or the **size threshold** for logging small
AI edits.
