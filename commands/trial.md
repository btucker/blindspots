---
name: trial
description: Run a blind user trial. A tool-restricted persona explores the product with no specs, no docs, no source code — only the browser. Discovers what the product does and documents it.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --fresh to start over"
---

# Blindspots — Trial

Run a blind user trial. A persona explores your product with zero context —
no specs, no docs, no source code. They discover what it does and write
specifications from observation.

## Step 1: Validate

Read `.blindspots/config.md`. Only needed for Setup, URL, and Specs sections.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona
- `--fresh` — clear previous trial output

## Step 3: Personas

Same as dogfood — generate `.blindspots/personas.md` if missing.

1. Read `README.md`, `.blindspots/config.md`, and resolved spec files (~2000 chars each)
2. Read persona template from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/persona-template.md`
3. Run 2-4 web searches about the target audience
4. Write `.blindspots/personas.md` with 5-6 personas + one anti-persona

## Step 4: Select Persona

Read `.blindspots/personas.md`. If `--persona` given, substring match. Otherwise random.
Print selected persona name and quote.

## Step 5: Setup

```bash
mkdir -p .blindspots/screenshots
```

Run setup commands from `## Setup` in `.blindspots/config.md`. Extract URL.

## Step 6: Launch

Launch the `trial-explorer` agent with ONLY:

```
The app is running at <URL>.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring. Write all output to .blindspots/.
```

Do NOT include content from config.md (explore ideas, diagnostics, specs).
The agent has no Read, Grep, or Glob tools — true isolation.

## Step 7: Compare

When the trial ends and `.blindspots/discovered-specs.md` exists, launch the
`trial-compare` agent with:
- Path to `.blindspots/discovered-specs.md`
- Path to `.blindspots/reactions.md`
- All resolved spec file paths from `## Specs` in config

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions:

```
- SPECS.md — main requirements
- docs/specs/*.md — design specs
```

Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
