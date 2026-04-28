# Dogfood — Testing Cycle

Test a product as a new user. Exercise the product, find bugs, fix the code,
and commit fixes.

## Environment

- **Worktree** (cwd) — an isolated git worktree for code changes
- **App** — the running product, accessible via Chrome browser tools
- **Source code** — available in the worktree for reading, testing, and fixing
- **`.blindspots/config.md`** — project-specific config (explore ideas,
  diagnostics, test conventions, spec references)
- **`.blindspots/`** — output directory for journal and screenshots

## Cycle

Follow this cycle each iteration.

### REBASE
Keep the worktree branch current with its base so fixes land on up-to-date
code and the branch doesn't drift over a long loop. The base ref was recorded
in git config when the worktree was created:

```bash
BASE=$(git config "branch.$(git branch --show-current).blindspots-base")
git fetch origin 2>/dev/null || true
git rebase "$BASE"
```

If `BASE` is empty (older worktrees), skip the rebase. If the rebase has
conflicts you can't confidently resolve, run `git rebase --abort`, note the
divergence in the journal, and continue the cycle on the un-rebased branch —
forward progress matters more than staying perfectly current.

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

### FIX
Fix the source code. If the project has a test framework (check .blindspots/config.md),
write a test and confirm it passes. Otherwise, verify the fix manually.

### COMMIT
Commit the fix to the worktree branch with a descriptive message.
Do NOT push or open a PR — just commit locally.

## Journal

Maintain your persona's dogfood journal at `.blindspots/dogfood-journals/<persona-slug>.md`.

**Start of each cycle**: read it.
**End of each cycle**: update with what was explored, what broke, what was
fixed, what to try next.

## Rules

- **One bug per cycle.** Find one, fix it, commit it, move on.
- **Spec first.** Always check the spec before fixing.
- **Screenshots as evidence.** Save to `.blindspots/screenshots/` when useful.
- **Stay curious.** Edge cases, error scenarios, rapid interactions.
- **Don't fix what isn't broken.** Move on to something else.
