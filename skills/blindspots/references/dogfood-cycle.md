# Dogfood — Testing Cycle

Test a product as a new user. Exercise the product, find bugs, write failing
tests, fix the code, and open PRs.

## Environment

- **Worktree** (cwd) — an isolated git worktree for code changes
- **App** — the running product, accessible via Chrome browser tools
- **Source code** — available in the worktree for reading, testing, and fixing
- **`.blindspots/config.md`** — project-specific config (explore ideas,
  diagnostics, test conventions, spec references)
- **`.blindspots/`** — output directory for journal and screenshots

## Cycle

Follow this cycle each iteration.

### EXPLORE
Read your persona's dogfood journal at `.blindspots/dogfood-journals/<persona-slug>.md`
(create it if missing) to see what was already tried.
Read `.blindspots/config.md` for exploration ideas. Pick something new.

### USE
Interact with the app through Chrome browser tools. Navigate, click, type, take
screenshots (save to `.blindspots/screenshots/`). Use CLI for diagnostics when the
UI behaves unexpectedly.

### DIAGNOSE
When something breaks:
1. Is this a real bug or user error? Check the specs listed in .blindspots/config.md.
2. Check the diagnostic sources listed in .blindspots/config.md (logs, console, etc.)
3. Identify the root cause in the source code.
4. Classify: UI bug, API bug, data bug, or spec gap.

### SPEC
If the spec does not cover the expected behavior, update it. Check .blindspots/config.md
for where specs live.

### RED
Write a failing test that reproduces the bug. Follow the test conventions in
.blindspots/config.md. Run it, confirm it fails.

### GREEN
Fix the source code. Run the test again — confirm it passes. Run the full test
suite to check for regressions.

### COMMIT
Commit the fix to the worktree branch with a descriptive message.
Do NOT push or open a PR — just commit locally.

## Journal

Maintain your persona's dogfood journal at `.blindspots/dogfood-journals/<persona-slug>.md`.

**Start of each cycle**: read it.
**End of each cycle**: update with what was explored, what broke, the PR, what
to try next.

## Rules

- **One bug per cycle.** Find one, fix it, commit it, move on.
- **Spec first.** Always check the spec before writing the test.
- **Screenshots as evidence.** Save to `.blindspots/screenshots/` when useful.
- **Stay curious.** Edge cases, error scenarios, rapid interactions.
- **Don't fix what isn't broken.** Move on to something else.
