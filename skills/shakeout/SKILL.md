---
name: shakeout
description: This skill should be used when the user is running an exploratory testing session, when "shakeout-journal.md" or "SHAKEOUT.md" exists in the project, when the user mentions "shakeout", "exploratory testing", or when working in a git branch starting with "shakeout/".
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
Test the product against known specs and requirements. The project's `SHAKEOUT.md`
defines what to explore, how to diagnose, and where specs live.

### Blind Mode
Explore with NO access to specs or documentation. Discover what the product does
and write specifications from observation. Produce `shakeout-discovered-specs.md`.

## Core Cycle

Each loop iteration follows one of two cycles depending on mode. Detailed cycle
instructions are in the references directory:

- **Guided**: `references/guided-cycle.md` — EXPLORE, USE, DIAGNOSE, SPEC, RED, GREEN, PR
- **Blind**: `references/blind-cycle.md` — EXPLORE, USE, OBSERVE, DOCUMENT, BUG

## Key Principles

- **One bug per cycle.** Find it, test it, fix it, PR it, move on.
- **Journal everything.** Read `shakeout-journal.md` at cycle start, update at end.
- **Screenshots as evidence.** Capture before diagnosing.
- **Spec first.** In guided mode, always check the spec before writing a test.
- **Stay in character.** The persona shapes exploration behavior.

## Project Files

| File | Purpose |
|------|---------|
| `SHAKEOUT.md` | Project-specific testing config (explore, diagnose, test sections) |
| `SHAKEOUT-PERSONAS.md` | Pool of user personas for testing |
| `shakeout-journal.md` | Session log (what was tried, what broke, PRs opened) |
| `shakeout-discovered-specs.md` | Blind mode output — discovered specifications |
| `shakeout-reactions.md` | Blind mode output — persona's emotional reactions (surprises, frustrations, delights) |
| `shakeout-comparison.md` | Blind mode output — discovered vs actual spec analysis |

## Comparison Agent

After a blind session, launch the `shakeout-compare` agent with the discovered
specs and actual specs paths. See `references/compare-prompt.md` for the
comparison methodology.

## Additional Resources

### Reference Files

- **`references/guided-cycle.md`** — Full guided cycle instructions
- **`references/blind-cycle.md`** — Full blind discovery cycle instructions
- **`references/compare-prompt.md`** — Spec comparison methodology
