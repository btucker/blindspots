---
name: experiment
description: A/B test two product variants with synthetic personas. Runs the same personas against both variants in parallel, then synthesizes a ship/no-ship verdict.
arguments:
  - name: options
    description: "<test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]"
---

# Blindspots — Experiment

A/B test two product variants with synthetic personas.

## Step 0: Depth Check

Check `BLINDSPOTS_DEPTH` environment variable. If >= 1, skip — inform the user
that nested experiment sessions are not supported.

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

Read `.blindspots/config.md`. If it does not exist, run the setup command (`blindspots:setup`) before continuing.

Read `.blindspots/personas.md`. If it does not exist, run the setup command (`blindspots:setup`) before continuing.

Select N personas (exclude anti-persona):
- If `--persona` given, use only that persona
- Otherwise pick N random (capped at persona count)
- Same personas run both variants (paired comparison)

## Step 2b: Infer Interface Mode

Determine which explorer agent to use:

1. **Check variant sources first**: if any variant source is a URL (starts with
   `http`), use **browser mode** — URL-based variants always need a browser.
2. **Check config override**: read `## Tools` from `.blindspots/config.md`. If it
   says `browser` or `terminal`, use that mode.
3. **Infer from start instructions**: read `## Start` from `.blindspots/config.md`
   (fall back to `## URL` for backward compat). If it contains a URL (starts with
   `http` or `localhost`), use **browser mode**. Otherwise use **terminal mode**.

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

Set depth before launching:

```bash
export BLINDSPOTS_DEPTH=1
```

Launch 2N explorer agents in parallel, using the agent matching the inferred mode:
- **Browser mode** → `user-trial-explorer-browser`
- **Terminal mode** → `user-trial-explorer-terminal`

For **browser mode**, each agent receives:

```
The app is running at <variant-url>.
Write all output to .blindspots/experiments/<test-name>/<label>/<persona-run>/.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring.
```

For **terminal mode**, each agent receives:

```
Write all output to .blindspots/experiments/<test-name>/<label>/<persona-run>/.

Your persona:
## <persona name>
<full persona description>

Start instructions:
<content from ## Start in .blindspots/config.md>
```

Wait for all agents to complete. Update manifest status to `complete`.

## Step 7: Verdict

Launch the `experiment-verdict` agent with:
- The experiment directory path (`.blindspots/experiments/<test-name>/`)
- All resolved spec file paths from `.blindspots/config.md`

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions.
Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
