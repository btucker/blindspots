---
name: experiment
description: A/B test two product variants with synthetic personas. Runs the same personas against both variants in parallel, then synthesizes a ship/no-ship verdict.
arguments:
  - name: options
    description: "<test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>] — all optional, prompts for missing values"
---

# Blindspots — Experiment

A/B test two product variants with synthetic personas.

## Step 0: Depth Check

Check `BLINDSPOTS_DEPTH` environment variable. If >= 1, skip — inform the user
that nested experiment sessions are not supported.

## Step 1: Validate

Read `.blindspots/config.md`. If it does not exist, run the setup command
(`blindspots:setup`) before continuing.

Read `.blindspots/personas.md`. If it does not exist, run the setup command
(`blindspots:setup`) before continuing.

## Step 2: Gather Parameters

Parse any arguments provided. For anything missing, ask interactively.

### Test name

If not given as first positional argument, ask:
"What should this experiment be called?" Suggest a name based on context
(e.g. the current branch name, recent commits).

### Variants

If two `<label>=<source>` pairs not given, ask:

1. "What's the first variant?" — ask for a label and source.
   Show source type examples:
   - URL: `http://localhost:3000`
   - Branch: `main`
   - Path: `~/projects/myapp`

2. "What's the second variant?" — same format.

When no `=` is present, the source is also the label.

Source type detection:
- Starts with `http` → URL
- Contains `/` or `.` → path
- Otherwise → branch

For path/branch sources, assign ports (3000 for first variant, 3001 for second,
or find free ports).

### Runs

If `--runs` not given, ask:
"How many personas per variant?" Default: 3.

### User type

Ask: "Should these be new users or returning users?"

- **New users** — personas explore with no prior context. Tests first impressions,
  onboarding, discoverability.
- **Returning users** — personas are loaded with context from a previous user trial
  or experiment (if available). Tests whether changes improve the experience for
  people who already know the product.

If returning users selected, check for existing session output in `.blindspots/`
and load the relevant journal/reactions as persona context.

### Personas

If `--persona` given, use only that persona.
Otherwise pick N random personas (capped at persona count, exclude anti-persona).
Same personas run both variants (paired comparison).

## Step 3: Infer Interface Mode

Determine which explorer agent to use:

1. **Check variant sources first**: if any variant source is a URL (starts with
   `http`), use **browser mode** — URL-based variants always need a browser.
2. **Check config override**: read `## Tools` from `.blindspots/config.md`. If it
   says `browser` or `terminal`, use that mode.
3. **Infer from start instructions**: read `## Start` from `.blindspots/config.md`
   (fall back to `## URL` for backward compat). If it contains a URL (starts with
   `http` or `localhost`), use **browser mode**. Otherwise use **terminal mode**.

## Step 4: Setup Variants

Resolve each variant:
- URL: verify reachable with `curl -s -o /dev/null -w "%{http_code}" <url>`
- Path: read `.blindspots/config.md` from path, run setup, start server
- Branch: create worktree from branch, read config, run setup, start server

## Step 5: Create Directories

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

## Step 6: Write Manifest

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

## Step 7: Launch All Agents in Parallel

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

## Step 8: Verdict

Launch the `experiment-verdict` agent with:
- The experiment directory path (`.blindspots/experiments/<test-name>/`)
- All resolved spec file paths from `.blindspots/config.md`

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions.
Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
