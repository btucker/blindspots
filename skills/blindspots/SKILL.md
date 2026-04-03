---
name: blindspots
description: This skill should be used when the user is running blindspots testing, when a ".blindspots/" directory exists in the project, when the user mentions "blindspots", "dogfood", "trial", "experiment", or "interview" in a testing context, or when working in a git branch starting with "blindspots/".
---

# Blindspots — Find Your Product's Blind Spots

This skill provides context and guidance during an active blindspots session.

## Modes

| Command | Purpose | Has Specs? | Fixes Bugs? |
|---------|---------|------------|-------------|
| `blindspots:dogfood` | Test against specs, find regressions | Yes | Yes |
| `blindspots:trial` | Blind persona discovers the product | No | No |
| `blindspots:experiment` | A/B compare two variants with blind personas | No | No |
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
| `.blindspots/discovered-specs.md` | trial | Specs from observation |
| `.blindspots/reactions.md` | trial | Persona emotional reactions |
| `.blindspots/comparison.md` | trial | Discovered vs actual analysis |
| `.blindspots/screenshots/` | all | Evidence |
| `.blindspots/experiments/<name>/` | experiment | A/B test output |
| `.blindspots/interviews/<name>.md` | interview | Interview transcripts |

## Agents

- **`trial-explorer`** — Browser-only agent for blind discovery. No Read/Grep/Glob.
- **`trial-compare`** — Analyzes discovered specs vs actual specs.
- **`experiment-verdict`** — Synthesizes A/B test results into ship/no-ship verdict.
- **`interviewer`** — Conducts persona Q&A sessions.

## Shared Steps

Several commands share common setup steps. These are documented in the commands
themselves but follow a consistent pattern:

1. Read `.blindspots/config.md`
2. Generate `.blindspots/personas.md` if missing (using `references/persona-template.md`)
3. Select persona (random or `--persona <name>`)
4. Run setup commands from config
5. Mode-specific launch

## Reference Files

- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → DIAGNOSE → RED → GREEN → PR)
- **`references/compare-prompt.md`** — Spec comparison methodology
- **`references/persona-template.md`** — Persona generation template
- **`references/experiment-verdict-prompt.md`** — A/B verdict methodology
