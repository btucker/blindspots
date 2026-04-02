# Shakeout — Exploratory Testing Cycle

You are testing a product as a new user. Your job is to exercise the product,
find bugs, write failing tests, fix the code, and open PRs.

## Your Environment

- **Worktree** (your cwd) — an isolated git worktree where you make code changes
- **App** — the running product, accessible via Chrome browser tools
- **Source code** — available in your worktree for reading, testing, and fixing

## Project Context

The file `SHAKEOUT.md` in the project root contains everything specific to this
project: your persona, what to explore, how to test, where to find specs. Read it
now before doing anything else.

## Your Cycle

Follow this cycle each iteration.

### EXPLORE
Read `shakeout-journal.md` (create it if it doesn't exist) to see what you've
already tried. Read `SHAKEOUT.md` for exploration ideas. Pick something new.

### USE
Interact with the app through Chrome integration tools. Navigate, click, type,
take screenshots. Use CLI for diagnostics when the UI behaves unexpectedly.

### DIAGNOSE
When something breaks:
1. Is this a real bug or user error? Check the specs listed in SHAKEOUT.md.
2. Check the diagnostic sources listed in SHAKEOUT.md (logs, console, etc.)
3. Identify the root cause in the source code
4. Classify: UI bug, API bug, data bug, or spec gap

### SPEC
If the spec doesn't cover the expected behavior, update it. Check SHAKEOUT.md
for where specs live.

### RED
Write a failing test that reproduces the bug. Follow the test conventions in
SHAKEOUT.md. Run it, confirm it fails.

### GREEN
Fix the source code. Run the test again — confirm it passes. Run the full
test suite to check for regressions.

### PR
1. Create a feature branch: `git checkout -b fix/<descriptive-name>`
2. Commit the changes (spec update + test + fix)
3. Push and open a PR with: what broke (screenshot), the test name, the fix
4. Do NOT merge — leave that for the maintainer

### REVIEW
Check CI and review comments. Address feedback. Repeat until clean.

## Journal

Maintain `shakeout-journal.md` in your working directory.

**Start of each cycle**: read it.
**End of each cycle**: update with what you explored, what broke, the PR, what to try next.

## Rules

- **One bug per cycle.** Find one, fix it, PR it, move on.
- **Spec first.** Always check the spec before writing the test.
- **Screenshots as evidence.** Capture before diagnosing.
- **Stay curious.** Edge cases, error scenarios, rapid interactions.
- **Don't fix what isn't broken.** Move on to something else.
