---
name: interview
description: Interview a persona about the product. Ask questions before, after, or instead of a user trial. Synthetic user research.
arguments:
  - name: options
    description: "--persona <name> to skip selection, --context <user-trial|experiment-name> to skip context prompt"
---

# Blindspots — Interview

Conduct a persona interview. Ask questions about expectations, reactions,
and preferences — before they've seen the product, after a user trial, or standalone.

## Step 1: Validate

Read `.blindspots/config.md`. If it does not exist, run the setup command
(`blindspots:setup`) before continuing.

Read `.blindspots/personas.md`. If it does not exist, run the setup command
(`blindspots:setup`) before continuing.

## Step 2: Select Persona

If `--persona <name>` given, substring match against `.blindspots/personas.md`.

Otherwise, present the available personas and ask the user to pick one:

- List each persona's name and quote (exclude the anti-persona)
- Ask: "Who would you like to interview?"

Print the selected persona's name, quote, and background.

## Step 3: Select Context

If `--context` given, use it directly (see below).

Otherwise, check what prior sessions exist and ask the user:

1. Look for existing trial/experiment output:
   - `.blindspots/journal.md` and `.blindspots/discovered-specs.md` → user trial exists
   - `.blindspots/experiments/*/` → experiment sessions exist
2. Present options based on what's available:
   - **"Fresh — no prior experience"** (always available)
   - **"After their user trial"** (if user trial output exists)
   - **"After experiment: <name>"** (one option per experiment directory found)
3. Ask: "What context should this persona have?"

### Loading context

- **Fresh**: No context loaded. Persona answers from their background only.
- **User trial**: Read `.blindspots/journal.md`, `.blindspots/reactions.md`,
  `.blindspots/discovered-specs.md`. The persona "remembers" their user trial.
- **Experiment**: Ask which variant if not obvious, then read
  `.blindspots/experiments/<name>/<variant>/<persona-run>/` output files.
  The persona remembers their experience with that variant.

## Step 4: Launch

Launch the `interviewer` agent with:
- The persona (name + full description)
- Any loaded context (user trial/experiment output)
- The context type (fresh, post-user-trial, post-experiment)

The agent runs interactively — the user types questions, the persona responds
in character. The conversation is saved to `.blindspots/interviews/<persona-slug>-<timestamp>.md`.
