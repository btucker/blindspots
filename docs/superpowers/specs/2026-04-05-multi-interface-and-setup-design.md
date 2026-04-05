# Multi-Interface Support and Auto-Setup

**Date:** 2026-04-05

## Problem

Blindspots assumes every product is a webapp. The explorer agent hardcodes Chrome
browser tools. The config requires a URL. This means you can't use blindspots on
CLI tools, Claude Code plugins, APIs, or anything that isn't a webapp.

Additionally, getting started requires manually creating `.blindspots/config.md`
and understanding the config format before you can run anything.

## Design

### Config changes

`## URL` becomes `## Start`. Freeform text that tells the persona how to begin
interacting with the product.

Examples:

```markdown
## Start
http://localhost:3000
```

```markdown
## Start
Run `mytool --help` in the terminal
```

```markdown
## Start
Read README.md, then try the slash commands
```

Backward compatibility: if `## Start` is missing but `## URL` exists, treat the
URL value as the start instructions.

Optional override: `## Tools: browser|terminal` forces a specific mode. If absent,
inferred from `## Start`.

### Tool set inference

The command reads `## Start` and selects a tool set:

- **Browser mode** — `## Start` contains a URL (starts with `http` or `localhost`).
  Browser tools + Bash (limited) + Write.
- **Terminal mode** — `## Start` does not contain a URL.
  Bash + Read + Write. Read restricted by prompt to files a real user would access.

### Two explorer agents

Instead of one dynamically configured agent, two purpose-built agents:

- **`user-trial-explorer-browser.md`** — renamed from `user-trial-explorer.md`.
  Hardcoded browser tools. Browser-specific instructions.
- **`user-trial-explorer-terminal.md`** — new. Bash + Read + Write. Terminal-specific
  instructions. Read restrictions are prompt-based: the persona may only read files
  mentioned in start instructions, files that commands point them to, and their own
  `.blindspots/` output.

Both share the same explore/use/observe/react/document/journal cycle. Some
duplication, but each agent file is self-contained and clear.

The command infers the mode from `## Start` and launches the right agent.

### Recursion depth limit

When blindspots launches an explorer agent, it sets:

```bash
export BLINDSPOTS_DEPTH=1
```

All blindspots commands check `BLINDSPOTS_DEPTH` at startup. If >= 1, the command
runs normally but does not spawn further blindspots agents. Commands that launch
explorer agents (`/user-trial`, `/experiment`, `/dogfood`) all set this variable
before launching. This allows a persona to run `/dogfood` during a user trial —
the dogfood session works, but doesn't nest another level.

### `/setup` command

Standalone command that generates `.blindspots/config.md` and
`.blindspots/personas.md` interactively.

**Flow:**

1. Read project context (README, package.json / pyproject.toml / Cargo.toml, docs)
2. Ask clarifying questions one at a time:
   - Product type (webapp, CLI, plugin, etc.)
   - How to start it (dev server, command name, etc.)
   - Where it runs (URL, terminal, etc.)
   - Spec file locations
3. Write `.blindspots/config.md`
4. Generate persona candidates from project context + web research
5. Present each persona to the user — name, background, quote, goals
6. User can tweak, drop, or approve each one
7. Write `.blindspots/personas.md` with the approved set

**Auto-run:** All commands (`/dogfood`, `/user-trial`, `/experiment`, `/interview`)
check for `.blindspots/config.md` on startup. If missing, they run the `/setup`
flow inline before continuing.

**Standalone use:** Run `/setup` directly to regenerate config after project changes.

Persona generation moves out of individual commands and into `/setup`. Commands
just read what's already there.

### README update

Getting started becomes:

```
/dogfood
```

One command. Config and personas are generated interactively on first run. The
Setup section in the README changes from "create this file" to explaining what
gets generated and how to customize it.

## What changes

**Config:**
- `## URL` renamed to `## Start` (backward compatible)
- Optional `## Tools: browser|terminal` override

**New files:**
- `commands/setup.md` — interactive config and persona generation
- `agents/user-trial-explorer-terminal.md` — terminal-mode explorer

**Renamed files:**
- `agents/user-trial-explorer.md` -> `agents/user-trial-explorer-browser.md`

**Modified files:**
- `commands/user-trial.md` — mode inference, agent selection
- `commands/experiment.md` — same inference and agent selection
- `commands/dogfood.md` — BLINDSPOTS_DEPTH check and set
- `README.md` — simplified getting started, `## Start` in config example

**No changes to:**
- Output format (journal, discovered-specs, reactions)
- Comparison agent (`user-trial-compare`)
- Interview command/agent
- Verdict agent
- Persona template
