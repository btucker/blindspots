---
name: shakeout
description: This skill should be used when the user is running an exploratory testing session, when a ".shakeout/" directory exists in the project, when the user mentions "shakeout" or "exploratory testing", or when working in a git branch starting with "shakeout/".
---

# Shakeout — Exploratory Testing Skill

This skill provides context and guidance during an active shakeout session. It
auto-activates when working in a shakeout context.

## Context

A shakeout is an automated exploratory testing loop where Claude acts as a real
user — navigating the product through the browser, finding bugs, writing failing
tests, fixing code, and opening PRs. Sessions run in isolated git worktrees.

## Modes

### Guided Mode
Test the product against known specs and requirements. The project's
`.shakeout/config.md` defines what to explore, how to diagnose, and where specs live.

### Blind Mode
A **separate agent** (`shakeout-blind`) explores with NO access to source code,
specs, or documentation. The agent's tools are restricted to browser interaction
and writing output files — it literally cannot read project files. This enforces
true isolation, not just an honor system.

## The .shakeout/ Directory

Everything lives in `.shakeout/`. Config and personas are checked in; session
output is gitignored.

### Config (checked in)

| File | Purpose |
|------|---------|
| `.shakeout/config.md` | Project-specific testing config (setup, URL, explore, diagnose, test, specs) |
| `.shakeout/personas.md` | Pool of user personas for testing |

### Output (gitignored)

| File | Mode | Purpose |
|------|------|---------|
| `.shakeout/journal.md` | Both | Session log (explored, found, PRs, next steps) |
| `.shakeout/discovered-specs.md` | Blind | Specifications discovered from observation |
| `.shakeout/reactions.md` | Blind | Persona's emotional reactions |
| `.shakeout/comparison.md` | Blind | Discovered vs actual spec analysis |
| `.shakeout/screenshots/` | Both | Evidence captured during exploration |

## Core Cycle

Detailed cycle instructions are in the references directory:

- **Guided**: `references/guided-cycle.md` — EXPLORE, USE, DIAGNOSE, SPEC, RED, GREEN, PR
- **Blind**: embedded in the `shakeout-blind` agent — EXPLORE, USE, OBSERVE, REACT, DOCUMENT

## Key Principles

- **One bug per cycle.** Find it, test it, fix it, PR it, move on.
- **Journal everything.** Read `.shakeout/journal.md` at start, update at end.
- **Screenshots as evidence.** Save to `.shakeout/screenshots/`.
- **Spec first.** In guided mode, check the spec before writing a test.
- **Stay in character.** The persona shapes exploration behavior.

## Agents

- **`shakeout-blind`** — Browser-only agent for blind discovery. No Read/Grep/Glob.
- **`shakeout-compare`** — Analyzes discovered specs vs actual specs after blind mode.

## Additional Resources

### Reference Files

- **`references/guided-cycle.md`** — Full guided cycle instructions
- **`references/compare-prompt.md`** — Spec comparison methodology
- **`references/persona-template.md`** — Template for generating personas
