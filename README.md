# Shakeout

A Claude Code plugin for automated exploratory testing. Claude acts as a real
user — navigating through the browser, finding bugs, writing tests, fixing code,
and opening PRs.

## Install

```bash
claude plugin add ~/projects/shakeout
```

Or test without installing:
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

The default. Claude gets the full `SHAKEOUT.md` — specs, exploration ideas — and
tests the product against known requirements.

**Finds**: bugs, regressions, spec violations, edge cases.

### Blind

Claude gets no specs, no docs, no requirements. It explores the product as a
completely naive first-time user and writes specifications from observation.

When the blind session ends, a comparison agent analyzes discovered specs against
the real ones, producing a report with:

- **Matched** — requirements discovered and spec'd
- **Undiscoverable** — spec'd features the user couldn't find (UX gaps)
- **Unspecified** — real behaviors missing from the specs
- **Expectation mismatches** — where the UI communicates different behavior than spec'd

**Finds**: UX discoverability problems, spec gaps, confusing flows.

## Personas

Each run is driven by a persona that shapes how Claude explores. If
`SHAKEOUT-PERSONAS.md` doesn't exist, the `/shakeout` command generates one
using Claude based on the project's README, specs, and SHAKEOUT.md.

- **Random** (default): picks a random persona each run
- **Named**: `--persona "power"` matches by substring
- **Fallback**: uses `## Persona` from SHAKEOUT.md, or a generic first-time user

## Project Setup

### SHAKEOUT.md

Add to your project root:

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
path/to/SPECS.md

## Reference
Pointers to specs, design docs, and other sources of truth.
```

### Sections

| Section | Required | Used in Blind | Purpose |
|---------|----------|---------------|---------|
| Setup | Yes | Yes | Install and start commands |
| URL | Yes | Yes | Where the app is running |
| Explore | Yes | No | What to test (with spec IDs) |
| Diagnose | Yes | No | Where to look when things break |
| Test | Yes | Yes | How to write and run tests |
| Specs | No | Yes (comparison) | Path to specs file for comparison |
| Reference | No | No | Docs and design specs |

## Output

### Guided mode
- `shakeout-journal.md` — log of what was explored and found
- PRs with failing tests + fixes

### Blind mode
- `shakeout-journal.md` — exploration log
- `shakeout-discovered-specs.md` — specs written from observation
- `shakeout-comparison.md` — discovered vs actual spec analysis
- PRs for any clear bugs found during exploration

## Plugin Structure

```
shakeout/
├── .claude-plugin/plugin.json   # Plugin manifest
├── commands/shakeout.md         # /shakeout command
├── agents/shakeout-compare.md   # Spec comparison agent
└── skills/shakeout/
    ├── SKILL.md                 # Auto-activates during sessions
    └── references/
        ├── guided-cycle.md      # Guided testing cycle
        ├── blind-cycle.md       # Blind discovery cycle
        └── compare-prompt.md    # Comparison methodology
```
