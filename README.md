# Shakeout

Exploratory testing loop for any project. A Claude Code session acts as a new user, exercises the product through the browser, finds bugs, writes failing tests, fixes the code, and opens PRs.

## Quick Start

```bash
# From any project with a SHAKEOUT.md:
~/projects/shakeout/shakeout.sh

# Or with explicit project path:
~/projects/shakeout/shakeout.sh --project ~/projects/offload
```

## How It Works

1. Reads `SHAKEOUT.md` from the target project for persona, setup, and exploration context
2. Starts the project's dev server (using the `setup` command from SHAKEOUT.md)
3. Creates an isolated git worktree for code changes
4. Launches a Claude Code session with Chrome integration
5. Runs the explore → diagnose → test → fix → PR cycle on a 10-minute loop

## Project Setup

Add a `SHAKEOUT.md` to your project root:

```markdown
# Project Name Shakeout

## Persona
Who is the test user? What's their background?

## Setup
How to install deps and start the dev server.

## URL
Where the app runs (e.g., http://localhost:3000).

## Explore
What features and flows to exercise.

## Diagnose
Where to look when things break (logs, console, etc.).

## Test
How to write and run tests (framework, conventions, commands).

## Reference
Specs, docs, and other sources of truth for expected behavior.
```

## Commands

```bash
shakeout.sh                    # run (or resume) the loop
shakeout.sh --fresh            # force a fresh session
shakeout.sh --setup            # just set up (don't start loop)
shakeout.sh --teardown         # just tear down
shakeout.sh --project <path>   # target a specific project
```
