---
name: user-trial
description: Run a user trial. A tool-restricted persona explores the product with no specs, no docs, no source code — only the browser or terminal. Discovers what the product does and documents it.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --fresh to start over"
---

# Blindspots — User Trial

Run a user trial. A persona explores your product with zero context —
no specs, no docs, no source code. They discover what it does and write
specifications from observation.

## Step 1: Validate

Check `BLINDSPOTS_DEPTH` environment variable. If >= 1, skip agent launching —
inform the user that nested blindspots sessions are not supported and stop.

Read `.blindspots/config.md`. If `.blindspots/config.md` does not exist, run
the `/setup` flow inline (invoke the `setup` command) before continuing.

Only needed for Setup, Start (or URL for backward compatibility), and Specs sections.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona
- `--fresh` — clear the selected persona's user trial directory to start over

## Step 3: Personas

Read `.blindspots/personas.md`. If it does not exist, run the setup command (`blindspots:setup`) before continuing.

## Step 4: Select Persona

Read `.blindspots/personas.md`. If `--persona` given, substring match. Otherwise random.
Print selected persona name and quote.

Derive persona slug: heading name lowercased, spaces to hyphens, tagline stripped.

## Step 5: Setup

```bash
mkdir -p .blindspots/user-trials/<persona-slug>/screenshots
```

If `--fresh`, delete contents of `.blindspots/user-trials/<persona-slug>/` first.

Run setup commands from `## Setup` in `.blindspots/config.md`.
Read `## Start` from config (or `## URL` for backward compatibility).

## Step 5.5: Mode Inference

Determine the interface mode from the config:

1. Read `## Start` from `.blindspots/config.md` (falling back to `## URL` for
   backward compatibility).
2. Check for an explicit override: if config contains `## Tools: browser` or
   `## Tools: terminal`, use that mode directly.
3. Otherwise, infer from the `## Start` content:
   - If it starts with `http` or `localhost` → **browser mode**
   - Otherwise → **terminal mode**

## Step 6: Launch

Set the depth guard before launching:

```bash
export BLINDSPOTS_DEPTH=1
```

Launch the explorer agent matching the inferred mode.

The output directory for this persona is `.blindspots/user-trials/<persona-slug>/`.
If a journal already exists there, this is a **return visit** — the persona
continues from where they left off.

### Browser mode

Launch the `user-trial-explorer-browser` agent with ONLY:

```
The app is running at <Start URL>.
Output directory: .blindspots/user-trials/<persona-slug>/

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring.
```

### Terminal mode

Launch the `user-trial-explorer-terminal` agent with ONLY:

```
Start instructions:
<full text from ## Start>
Output directory: .blindspots/user-trials/<persona-slug>/

Your persona:
## <persona name>
<full persona description>

Follow the start instructions and begin exploring.
```

Do NOT include content from config.md (explore ideas, diagnostics, specs).
The agents have restricted tools — true isolation.

## Step 7: Compare

When the user trial ends and `.blindspots/user-trials/<persona-slug>/discovered-specs.md`
exists, launch the `user-trial-compare` agent with:
- Path to `.blindspots/user-trials/<persona-slug>/discovered-specs.md`
- Path to `.blindspots/user-trials/<persona-slug>/reactions.md`
- All resolved spec file paths from `## Specs` in config

## Step 8: Generate HTML report

After comparison (or directly after exploration if no specs were configured),
emit a self-contained HTML report. Run:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/generate_trial_report.py" \
  ".blindspots/user-trials/<persona-slug>/"
```

The script reads `journal.md`, `discovered-specs.md`, `reactions.md`, and
`comparison.md` (whichever exist), embeds every PNG/JPG from `screenshots/`
as base64 `data:` URIs, and renders a Mermaid `journey` diagram from the
ordered reactions. Output: `.blindspots/user-trials/<persona-slug>/report.html`.

The file is single-file shareable — just attach it. Mermaid loads from CDN at
view time; offline viewers get a fallback note with the raw diagram source.

If `uv` is not installed, skip this step and tell the user how to get it
(`curl -LsSf https://astral.sh/uv/install.sh | sh`).

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions:

```
- SPECS.md — main requirements
- docs/specs/*.md — design specs
```

Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
