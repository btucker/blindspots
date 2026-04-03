---
name: interview
description: Interview a persona about the product. Ask questions before, after, or instead of a trial. Synthetic user research.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --context <trial|experiment-name> to load prior experience"
---

# Blindspots — Interview

Conduct a persona interview. Ask questions about expectations, reactions,
and preferences — before they've seen the product, after a trial, or standalone.

## Step 1: Personas

Generate `.blindspots/personas.md` if missing (same as other commands).

1. Read `README.md`, `.blindspots/config.md`, and resolved spec files (~2000 chars each)
2. Read persona template from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/persona-template.md`
3. Run 2-4 web searches about the target audience
4. Write `.blindspots/personas.md` with 5-6 personas + one anti-persona

## Step 2: Parse Arguments

- `--persona <name>` — required for interview (must specify who to talk to)
- `--context trial` — load this persona's prior trial output (journal, reactions,
  discovered specs) to give them memory of the experience
- `--context <experiment-name>` — load this persona's experiment output for a
  specific variant (will be asked which variant)
- No `--context` — persona answers from their background only (pre-trial interview)

## Step 3: Select Persona

Read `.blindspots/personas.md`, find the named persona. Print their name, quote,
and background.

## Step 4: Load Context (if applicable)

If `--context trial`:
- Read `.blindspots/journal.md`, `.blindspots/reactions.md`, `.blindspots/discovered-specs.md`
- The persona now "remembers" their trial experience

If `--context <experiment-name>`:
- Ask which variant to load context from
- Read `.blindspots/experiments/<name>/<variant>/<persona-run>/` output files
- The persona remembers their experience with that variant

## Step 5: Launch

Launch the `interviewer` agent with:
- The persona (name + full description)
- Any loaded context (trial/experiment output)
- Whether this is pre-trial, post-trial, or standalone

The agent runs interactively — the user types questions, the persona responds
in character. The conversation is saved to `.blindspots/interviews/<persona-slug>-<timestamp>.md`.
