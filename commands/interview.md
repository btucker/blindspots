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

Check `BLINDSPOTS_DEPTH` environment variable. If >= 1, skip — inform the user
that nested interview sessions are not supported and stop.

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

1. Look for existing trial/experiment/dogfood output for this persona:
   - `.blindspots/user-trials/<persona-slug>/discovered-specs.md` → user trial exists
   - `.blindspots/experiments/*/` → experiment sessions exist
   - `.blindspots/dogfood-journals/<persona-slug>.md` → this persona has dogfooded before
2. Present options based on what's available:
   - **"Fresh — no prior experience"** (always available)
   - **"After their user trial"** (if this persona's user trial output exists)
   - **"After experiment: <name>"** (one option per experiment directory found)
   - **"After dogfooding"** (if this persona's dogfood journal exists)
3. Ask: "What context should this persona have?"

### Loading context

- **Fresh**: No context loaded. Persona answers from their background only.
- **User trial**: Read `.blindspots/user-trials/<persona-slug>/journal.md`,
  `.blindspots/user-trials/<persona-slug>/reactions.md`, and
  `.blindspots/user-trials/<persona-slug>/discovered-specs.md`.
  The persona "remembers" their user trial.
- **Dogfood**: Read `.blindspots/dogfood-journals/<persona-slug>.md`. The persona
  remembers the bugs they found and what they explored.
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
