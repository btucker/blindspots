---
name: blindspots
description: This skill should be used when the user is running blindspots testing, when a ".blindspots/" directory exists in the project, when the user mentions "blindspots", "dogfood", "user-trial", "experiment", or "interview" in a testing context, or when working in a git branch starting with "blindspots/".
---

# Blindspots — Find Your Product's Blind Spots

This skill provides context and guidance during an active blindspots session.

## Modes

| Command | Purpose | Has Specs? | Fixes Bugs? |
|---------|---------|------------|-------------|
| `blindspots:setup` | Interactive config and persona generation | N/A | No |
| `blindspots:dogfood` | Test against specs, find regressions | Yes | Yes |
| `blindspots:user-trial` | Persona discovers the product with no insider knowledge | No | No |
| `blindspots:experiment` | A/B compare two variants with user trial personas | No | No |
| `blindspots:interview` | Ask personas questions about the product | Depends | No |

## The .blindspots/ Directory

Config is checked in; session output is gitignored.

### Config (checked in)

| File | Purpose |
|------|---------|
| `.blindspots/config.md` | Project testing config (setup, URL, explore, diagnose, test, specs) |
| `.blindspots/personas.md` | Pool of user personas |

### Output (gitignored)

| File | Mode | Purpose |
|------|------|---------|
| `.blindspots/journal.md` | dogfood | Session log |
| `.blindspots/discovered-specs.md` | user-trial | Specs from observation |
| `.blindspots/reactions.md` | user-trial | Persona emotional reactions |
| `.blindspots/comparison.md` | user-trial | Discovered vs actual analysis |
| `.blindspots/screenshots/` | all | Evidence |
| `.blindspots/experiments/<name>/` | experiment | A/B test output |
| `.blindspots/interviews/<name>.md` | interview | Interview transcripts |

## Agents

- **`user-trial-explorer-browser`** — Browser-based user trial explorer. No Read/Grep/Glob.
- **`user-trial-explorer-terminal`** — Terminal-based user trial explorer. Bash + Read (restricted) + Write.
- **`user-trial-compare`** — Analyzes discovered specs vs actual specs.
- **`experiment-verdict`** — Synthesizes A/B test results into ship/no-ship verdict.
- **`interviewer`** — Conducts persona Q&A sessions.

## Shared Steps

All commands auto-run `/setup` if `.blindspots/config.md` is missing. The shared
startup pattern:

1. Check for `.blindspots/config.md` — run `blindspots:setup` if missing
2. Check for `.blindspots/personas.md` — run `blindspots:setup` if missing
3. Select persona (random or `--persona <name>`)
4. Run setup commands from config
5. Infer interface mode from `## Start` (browser or terminal)
6. Mode-specific launch with `BLINDSPOTS_DEPTH=1`

## Reference Files

- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → DIAGNOSE → RED → GREEN → PR)
- **`references/compare-prompt.md`** — Spec comparison methodology
- **`references/persona-template.md`** — Persona generation template
- **`references/experiment-verdict-prompt.md`** — A/B verdict methodology
