# Shakeout

Automated exploratory testing powered by Claude Code. A Claude session acts as a
real user — navigating through the browser, finding bugs, writing tests, fixing
code, and opening PRs.

## Quick Start

```bash
# Guided shakeout (specs-aware):
./shakeout.py --project ~/projects/myapp

# Blind shakeout (no specs — discovery mode):
./shakeout.py --blind --project ~/projects/myapp

# Pick a specific persona:
./shakeout.py --blind --persona "senior" --project ~/projects/myapp
```

## Modes

### Guided

The default mode. Claude gets the full `SHAKEOUT.md` — specs, exploration
ideas — and tests the product against known requirements.

**Finds**: bugs, regressions, spec violations, edge cases.

### Blind

Claude gets no specs, no docs, no requirements. It explores the product as a
completely naive first-time user and writes specifications based on what it
discovers.

When the blind session ends, a second Claude session automatically launches to
compare the discovered specs against the real ones, producing a report with:

- **Matched** — requirements discovered and spec'd
- **Undiscoverable** — spec'd features the user couldn't find (UX gaps)
- **Unspecified** — real behaviors missing from the specs
- **Expectation mismatches** — where the UI suggests different behavior than spec'd

**Finds**: UX discoverability problems, spec gaps, confusing flows.

## Personas

Each shakeout run is driven by a persona — a character that shapes how Claude
explores, what it notices, and what frustrates it. Different personas find
different bugs.

### SHAKEOUT-PERSONAS.md

Create this file in your project root with one `##` section per persona:

```markdown
# Shakeout Personas

## Overwhelmed Sophomore
You are a college sophomore using the app for the first time. You tend to click
around tentatively and get confused by jargon.

## Power User
You are a returning user who knows exactly what they want. You move fast, use
keyboard shortcuts, and get annoyed by unnecessary steps.

## Accessibility Tester
You navigate primarily with a keyboard and screen reader. You care about focus
order, ARIA labels, and whether the app is usable without a mouse.
```

### Selection

- **Random** (default): each run picks a random persona from the file
- **Named**: `--persona "power"` matches by substring (case-insensitive)
- **Fallback**: if no `SHAKEOUT-PERSONAS.md` exists, uses `## Persona` from
  `SHAKEOUT.md`, or a generic first-time user

The selected persona is printed at launch so you know who's testing.

## How It Works

1. Reads `SHAKEOUT.md` from the target project
2. Runs setup commands (install deps, start dev server)
3. Selects a persona from `SHAKEOUT-PERSONAS.md`
4. Creates an isolated git worktree for code changes
5. Launches Claude Code with Chrome browser integration
6. Runs an explore → test → fix → PR cycle on a 10-minute loop

In blind mode, step 6 uses a discovery-focused prompt instead, and adds a spec
comparison phase after exploration ends.

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
| Specs | No | Yes (comparison) | Path to the specs file for comparison |
| Reference | No | No | Docs and design specs |

### SHAKEOUT-PERSONAS.md

One `## Name` section per persona. See [Personas](#personas) above.

## Commands

```bash
shakeout.py                            # run in current directory
shakeout.py --project <path>           # target a specific project
shakeout.py --blind                    # blind discovery mode
shakeout.py --persona <name>           # pick a specific persona
shakeout.py --fresh                    # discard previous session
shakeout.py --setup                    # just set up (don't start loop)
shakeout.py --teardown                 # stop server, clean up state
```

Flags combine: `./shakeout.py --blind --fresh --persona "advisor" --project ~/projects/myapp`

## Output

### Guided mode
- `shakeout-journal.md` — log of what was explored and found
- PRs with failing tests + fixes

### Blind mode
- `shakeout-journal.md` — exploration log
- `shakeout-discovered-specs.md` — specs written from observation
- `shakeout-comparison.md` — discovered vs actual spec analysis
- PRs for any clear bugs found during exploration
