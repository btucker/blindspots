# Dogfood Wrap-up and Panel Interview

**Date:** 2026-04-05

## Problem

The dogfood cycle assumes PRs are the delivery mechanism for fixes. It tells
the agent to push and open a PR after every bug fix. This is prescriptive —
not everyone uses GitHub, has `gh` installed, or wants PRs for every fix.

The interview command also lacks a "panel" mode where all personas react to
the same prompt at once, which turned out to be valuable for getting fast,
multi-perspective feedback on designs.

## Design

### 1. Dogfood cycle: commit only

The dogfood cycle reference file (`dogfood-cycle.md`) changes its PR step to
a COMMIT step:

**Before:**
```
### PR
1. Create a feature branch
2. Commit the changes
3. Push and open a PR
4. Do NOT merge
```

**After:**
```
### COMMIT
Commit the fix to the worktree branch with a descriptive message.
Do NOT push or open a PR — just commit locally.
```

The rules line changes from "find one, fix it, PR it, move on" to
"find one, fix it, commit it, move on."

The REVIEW step (check CI and review comments) is removed — there's no PR
to review during the loop.

### 2. Dogfood command: wrap-up on stop

The `/dogfood` command adds a **Step 8: Wrap-up** that runs after the loop
ends (user cancels or the cycle runs out of things to find).

**Wrap-up sequence:**

1. Remove the worktree: `git worktree remove .worktrees/<branch>`
2. Return to the project root (the original working directory before the
   worktree was created)
3. Print a summary:
   - Branch name
   - Number of commits (from `git log main..<branch> --oneline`)
   - Files changed (from `git diff main..<branch> --stat`)
   - One-line description of each fix from the journal
4. Present two options:
   - **Switch to the branch** — `git checkout <branch>` so the user can
     review the changes in their normal environment
   - **Run the finishing workflow** — invoke `finishing-a-development-branch`
     which handles PR creation, merge, or cleanup depending on the user's
     preferences and git setup

The branch survives worktree removal because `git worktree remove` doesn't
delete the branch — it just removes the working directory.

### 3. What doesn't change

- Worktree creation in Step 6 stays — isolation during the loop is still
  valuable (the user can keep working in their main checkout)
- `git fetch origin` stays — already handles missing remote gracefully
- The journal is maintained per-persona in `.blindspots/dogfood-journals/`

### 4. Panel interview

The `/interview` command adds "Panel — all personas" as the first option
when presenting the persona list.

**Current flow:**
```
Who would you like to interview?
1. Priya — "I don't have a QA team..."
2. Marcus — "Show me a tool..."
...
```

**New flow:**
```
Who would you like to interview?
1. Panel — all personas react to your question at once
2. Priya — "I don't have a QA team..."
3. Marcus — "Show me a tool..."
...
```

When "Panel" is selected:

- The interview runs in the main session (no subagent — panel responses are
  short enough to generate inline)
- For each user question, every persona (excluding the anti-persona) responds
  with 2-4 sentences in character
- Responses are presented under the persona's name and quote
- The conversation is saved to `.blindspots/interviews/panel-<timestamp>.md`

Panel mode does not support `--context` (loading prior trial/experiment
experience). Each persona responds from their background only. If the user
wants context-loaded responses, they should interview personas individually.

### 5. Interview command: context selection

The context step now checks for dogfood journals too:

```
1. Fresh — no prior experience
2. After their user trial (if output exists)
3. After dogfooding (if this persona's dogfood journal exists)
4. After experiment: <name> (one per experiment found)
```

This was already partially implemented but is confirmed as part of this spec.

## Files to change

| File | Change |
|------|--------|
| `skills/blindspots/references/dogfood-cycle.md` | PR → COMMIT, remove REVIEW |
| `commands/dogfood.md` | Add Step 8: Wrap-up |
| `commands/interview.md` | Add panel option to persona selection |
| `agents/interviewer.md` | Note panel mode behavior (or handle inline) |
| `skills/blindspots/SKILL.md` | Update dogfood cycle description |
