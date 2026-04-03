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

Read `.blindspots/config.md`. If missing, tell the user to create one with
sections: Setup, URL, Explore, Diagnose, Test, Specs.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona (substring match, case-insensitive)
- `--fresh` — delete `.blindspots/journal.md` to start fresh

## Step 3: Personas

If `.blindspots/personas.md` does not exist, generate it:

1. Read `README.md`, `.blindspots/config.md`, and resolved spec files (~2000 chars each)
2. Read persona template from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/persona-template.md`
3. Run 2-4 web searches about the target audience demographics and pain points
4. Write `.blindspots/personas.md` with 5-6 personas + one anti-persona

## Step 4: Select Persona

Read `.blindspots/personas.md`. If `--persona` given, substring match. Otherwise random.
Print selected persona name and quote.

## Step 5: Setup

```bash
mkdir -p .blindspots/screenshots
```

Run setup commands from `## Setup` in `.blindspots/config.md`.
Extract URL from `## URL` (default `http://localhost:3000`).

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
