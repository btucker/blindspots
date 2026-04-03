# Shakeout

A Claude Code plugin for automated exploratory testing. Claude acts as a real
user — navigating through the browser, finding bugs, writing tests, fixing code,
and opening PRs.

## Install

```bash
claude --plugin-dir ~/projects/shakeout
```

## Usage

```bash
/shakeout                          # guided mode, random persona
/shakeout --blind                  # blind discovery mode
/shakeout --persona "senior"       # pick a specific persona
/shakeout --blind --persona "advisor" --fresh
```

## Modes

### Guided

The default. Claude gets the full `.shakeout/config.md` — specs, exploration
ideas — and tests the product against known requirements.

**Finds**: bugs, regressions, spec violations, edge cases.

### Blind

A separate **`shakeout-blind` agent** explores the product with tool-level
isolation — it has browser access and Write only. No Read, no Grep, no Glob. It
literally cannot open source code, specs, or documentation. This is enforced by
the agent's tool restrictions, not just instructions.

When the blind session ends, a comparison agent analyzes discovered specs against
the real ones, producing a report with:

- **Matched** — requirements discovered and spec'd
- **Undiscoverable** — spec'd features the user couldn't find (UX gaps)
- **Unspecified** — real behaviors missing from the specs
- **Expectation mismatches** — where the UI communicates different behavior than spec'd

**Finds**: UX discoverability problems, spec gaps, confusing flows.

## Personas

Each run is driven by a persona that shapes how Claude explores. If
`.shakeout/personas.md` doesn't exist, the `/shakeout` command generates one
using Claude — grounded in web research about the product's target audience.

- **Random** (default): picks a random persona each run
- **Named**: `--persona "power"` matches by substring
- **Fallback**: uses a generic first-time user

## Project Setup

Create a `.shakeout/` directory in your project with a `config.md`:

```markdown
# My App Shakeout

## Setup
\```bash
npm install
npm run dev &
\```

## URL
http://localhost:3000

## Explore
What features and flows to exercise. Reference spec IDs where possible.

## Diagnose
Where to look when things break (logs, console, API endpoints).

## Test
Framework, import conventions, how to run tests.

## Specs
- SPECS.md — main requirements
- docs/specs/*.md — design specs
- docs/plans/*.md — implementation plans

## Reference
Pointers to specs, design docs, and other sources of truth.
```

### Config Sections

| Section | Required | Used in Blind | Purpose |
|---------|----------|---------------|---------|
| Setup | Yes | Yes (via command) | Install and start commands |
| URL | Yes | Yes (via command) | Where the app is running |
| Explore | Yes | No | What to test (with spec IDs) |
| Diagnose | Yes | No | Where to look when things break |
| Test | Yes | No | How to write and run tests |
| Specs | No | Yes (comparison) | Paths/globs to spec files (one per line) |
| Reference | No | No | Docs and design specs |

## The .shakeout/ Directory

Everything shakeout-related lives in `.shakeout/`. Config is checked in, session
output is gitignored.

```
.shakeout/
├── config.md              # checked in — project testing config
├── personas.md            # checked in — generated user personas
├── .gitignore             # ignores session output below
├── journal.md             # session log
├── discovered-specs.md    # blind mode — specs from observation
├── reactions.md           # blind mode — persona emotional responses
├── comparison.md          # blind mode — discovered vs actual analysis
└── screenshots/           # evidence captured during testing
```

## Plugin Structure

```
shakeout/
├── .claude-plugin/plugin.json       # Plugin manifest
├── commands/shakeout.md             # /shakeout command
├── agents/
│   ├── shakeout-blind.md            # Blind agent (browser-only, no Read/Grep/Glob)
│   └── shakeout-compare.md          # Spec comparison agent
└── skills/shakeout/
    ├── SKILL.md                     # Auto-activates during sessions
    └── references/
        ├── guided-cycle.md          # Guided testing cycle
        ├── compare-prompt.md        # Comparison methodology
        └── persona-template.md      # Persona generation template
```
