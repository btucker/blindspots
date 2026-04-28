---
name: blindspots
description: This skill should be used when the user is running blindspots testing, when a ".blindspots/" directory exists in the project, when the user mentions "blindspots", "dogfood", "user-trial", "experiment", or "interview" in a testing context, or when working in a git branch starting with "blindspots/".
---

# Blindspots — Find Your Product's Blind Spots

This skill provides context and guidance during an active blindspots session in Codex.

## Modes

| Mode | Purpose | Has Specs? | Fixes Bugs? |
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
| `.blindspots/config.md` | Project testing config (setup, start, explore, diagnose, test, specs) |
| `.blindspots/personas.md` | Pool of user personas |

### Output (gitignored)

| File | Mode | Purpose |
|------|------|---------|
| `.blindspots/dogfood-journals/<persona>.md` | dogfood | Per-persona session log |
| `.blindspots/user-trials/<persona>/` | user-trial | Per-persona trial output (journal, discovered-specs, reactions, comparison) |
| `.blindspots/screenshots/` | all | Evidence |
| `.blindspots/experiments/<name>/` | experiment | A/B test output |
| `.blindspots/interviews/<name>.md` | interview | Interview transcripts |

## Roles

- **Browser explorer** — Browser-based user trial explorer. Avoid source-code inspection.
- **Terminal explorer** — Terminal-based user trial explorer. Use shell and limited file reads.
- **Trial comparer** — Analyzes discovered specs vs actual specs.
- **Experiment verdict** — Synthesizes A/B test results into ship/no-ship verdict.
- **Interviewer** — Conducts persona Q&A sessions.

## Shared Steps

When the user asks for any Blindspots mode, first make sure setup exists. The
shared startup pattern:

1. Check for `.blindspots/config.md` — run `blindspots:setup` if missing
2. Check for `.blindspots/personas.md` — run `blindspots:setup` if missing
3. Select persona — method varies by mode:
   - `blindspots:dogfood`, `blindspots:user-trial`: random, or requested persona
   - `blindspots:interview`: show persona list and ask user to pick
   - `blindspots:experiment`: prompt interactively for test name, variants, user type, and run count
4. Run setup commands from config
5. Infer interface mode from `## Start` (browser or terminal)
6. Mode-specific launch with `BLINDSPOTS_DEPTH=1`

## Reference Files

- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → USE → DIAGNOSE → FIX → COMMIT)
- **`references/compare-prompt.md`** — Spec comparison methodology
- **`references/persona-template.md`** — Persona generation template
- **`references/experiment-verdict-prompt.md`** — A/B verdict methodology
