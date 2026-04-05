---
name: dogfood
description: Dogfood your product against its specs. Runs a persona-driven testing loop that explores, finds bugs, writes failing tests, fixes code, and opens PRs.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --fresh to start over"
---

# Blindspots — Dogfood

Test your product against its own specifications. Find bugs, write tests, fix code.

## Step 1: Validate

Read `.blindspots/config.md`. If it does not exist, run the setup command (`blindspots:setup`) before continuing.

Check `BLINDSPOTS_DEPTH` environment variable. If >= 1, run the dogfood cycle directly without launching subagents or worktrees — just do the testing work in the current session.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona (substring match, case-insensitive)
- `--fresh` — delete the selected persona's dogfood journal to start fresh

## Step 3: Personas

Read `.blindspots/personas.md`. If it does not exist, run the setup command (`blindspots:setup`) before continuing.

## Step 4: Select Persona

Read `.blindspots/personas.md`. If `--persona` given, substring match. Otherwise random.
Print selected persona name and quote.

## Step 5: Setup

```bash
mkdir -p .blindspots/screenshots .blindspots/dogfood-journals
```

Run setup commands from `## Setup` in `.blindspots/config.md`.
Extract the start point from `## Start` in `.blindspots/config.md` (fall back to `## URL` for backward compatibility; default `http://localhost:3000`).

## Step 6: Worktree

```bash
git fetch origin 2>/dev/null || true
BRANCH="blindspots/dogfood/$(date +%Y%m%d-%H%M%S)"
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main 2>/dev/null || git rev-parse HEAD)
git worktree add ".worktrees/$BRANCH" -b "$BRANCH" "$BASE"
cd ".worktrees/$BRANCH"
mkdir -p .blindspots/screenshots
```

## Step 7: Launch

Read cycle prompt from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/dogfood-cycle.md`.

Set `export BLINDSPOTS_DEPTH=1` before invoking the loop.

Prepend persona:

```
## Your Persona: <name>

<description>

Stay in character. Your persona shapes how you explore, what you notice, what frustrates you.

---

<cycle prompt>
```

Invoke: `/loop 10m <full prompt>`

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions:

```
- SPECS.md — main requirements
- docs/specs/*.md — design specs
```

Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
