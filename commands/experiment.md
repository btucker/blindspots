---
name: experiment
description: A/B test two product variants with blind personas. Runs the same personas against both variants in parallel, then synthesizes a ship/no-ship verdict.
arguments:
  - name: options
    description: "<test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]"
---

# Blindspots — Experiment

A/B test two product variants with blind personas.

## Step 1: Parse Arguments

```
blindspots:experiment <test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]
```

- `<test-name>` — names the experiment directory
- `<label>=<source>` — two variant specs. Source types:
  - URL (starts with `http`) → use directly
  - Path (contains `/` or `.`) → read `.blindspots/config.md`, run setup, start server
  - Branch (otherwise) → create worktree, read config, run setup, start server
- `--runs N` (default 3) — personas per variant (2N total agents)
- `--persona <name>` — run only this persona (2 agents total, for debugging)

When no `=` present, the source is also the label.

For path/branch sources, assign ports (3000 for first variant, 3001 for second,
or find free ports).

## Step 2: Personas

Generate `.blindspots/personas.md` if missing (same as other commands).

Select N personas (exclude anti-persona):
- If `--persona` given, use only that persona
- Otherwise pick N random (capped at persona count)
- Same personas run both variants (paired comparison)

## Step 3: Setup Variants

Resolve each variant:
- URL: verify reachable with `curl -s -o /dev/null -w "%{http_code}" <url>`
- Path: read `.blindspots/config.md` from path, run setup, start server
- Branch: create worktree from branch, read config, run setup, start server

## Step 4: Create Directories

```
.blindspots/experiments/<test-name>/
├── manifest.md
├── <variant-a-label>/
│   ├── <persona-slug>-<run>/
│   │   └── (journal.md, discovered-specs.md, reactions.md, screenshots/)
│   └── ...
├── <variant-b-label>/
│   └── ...
└── verdict.md
```

Persona slug: heading name lowercased, spaces to hyphens, tagline stripped.
Run number: 1-based, same number on both variants for pairing.

## Step 5: Write Manifest

Write `.blindspots/experiments/<test-name>/manifest.md`:

```markdown
# Experiment: <test-name>

- **Date**: <today>
- **Variant A**: <label> (<url>)
- **Variant B**: <label> (<url>)
- **Personas**: <name> (<run>), ...
- **Runs per variant**: <N>
- **Total agents**: <2N>
- **Status**: running
```

## Step 6: Launch All Agents in Parallel

Launch 2N `user-trial-explorer` agents in parallel. Each receives:

```
The app is running at <variant-url>.
Write all output to .blindspots/experiments/<test-name>/<label>/<persona-run>/.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring.
```

Wait for all agents to complete. Update manifest status to `complete`.

## Step 7: Verdict

Launch the `experiment-verdict` agent with:
- The experiment directory path (`.blindspots/experiments/<test-name>/`)
- All resolved spec file paths from `.blindspots/config.md`

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions.
Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
