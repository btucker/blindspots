# A/B Testing with Blind Personas

## Overview

Add A/B testing to shakeout: run the same blind personas against two product
variants in parallel, then synthesize the results into a ship/no-ship verdict.

The goal is to help product teams decide whether a change is worth rolling out —
using quantitative metrics (discovery rates, reaction counts) and qualitative
analysis (per-persona paired comparisons, regressions, improvements).

## Invocation

```
/shakeout --ab <test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]
```

### Variant Sources

Each variant is `<label>=<source>` where source is one of:

| Source type | Detection | Example | What shakeout does |
|-------------|-----------|---------|-------------------|
| URL | Starts with `http` | `main=http://localhost:3000` | Uses directly |
| Path | Contains `/` or `.` | `main=~/projects/offload` | Reads `.shakeout/config.md`, runs setup, starts server |
| Branch | Otherwise | `main` | Creates worktree, reads config, runs setup, starts server |

For path/branch variants, shakeout assigns ports automatically (3000 for first
variant, 3001 for second, or finds free ports).

### Arguments

| Argument | Default | Purpose |
|----------|---------|---------|
| `--ab <test-name>` | — | Enables A/B mode, names the test directory |
| `<label>=<source>` (×2) | — | The two variants to compare |
| `--runs N` | 3 | Personas per variant (2N total agents) |
| `--persona <name>` | random | Run only this persona (2 total agents, for debugging) |

### Examples

```bash
# Two URLs, 3 personas each
/shakeout --ab onboarding-redesign main=http://localhost:3000 new-onboarding=http://localhost:3001

# Two branches, 4 personas each
/shakeout --ab search-filters main feature/search-v2 --runs 4

# Two URLs, single persona for quick debugging
/shakeout --ab mobile-layout main=http://localhost:3000 mobile=http://localhost:3001 --persona "amara"
```

When no `=` is present in a variant spec, the source value is also used as the
label (e.g., `main` becomes both label and branch name).

## Persona Selection

1. Read `.shakeout/personas.md`, exclude the anti-persona section
2. If `--persona <name>` is specified, use only that persona
3. Otherwise pick N personas at random (capped at actual persona count)
4. The **same personas** run against both variants — paired comparison

## Directory Structure

```
.shakeout/ab/
└── onboarding-redesign/             # test name
    ├── manifest.md                  # test metadata
    ├── main/                        # variant A label
    │   ├── marcus-1/                # persona-slug + run number
    │   │   ├── journal.md
    │   │   ├── discovered-specs.md
    │   │   ├── reactions.md
    │   │   └── screenshots/
    │   ├── priya-2/
    │   │   └── ...
    │   └── deshawn-3/
    │       └── ...
    ├── new-onboarding/              # variant B label
    │   ├── marcus-1/                # same run numbers = paired
    │   ├── priya-2/
    │   └── deshawn-3/
    └── verdict.md                   # synthesis report
```

**Persona slug**: heading name lowercased, spaces to hyphens, tagline stripped
(e.g., "Marcus — The Reluctant Sophomore" → `marcus`).

**Run number**: 1-based sequential index across the test. Same persona gets the
same run number on both variants, making the pairing explicit.

## Manifest

Written before agents launch. Updated after completion.

```markdown
# A/B Test: onboarding-redesign

- **Date**: 2026-04-03
- **Variant A**: main (http://localhost:3000)
- **Variant B**: new-onboarding (http://localhost:3001)
- **Personas**: Marcus (1), Priya (2), DeShawn (3)
- **Runs per variant**: 3
- **Total agents**: 6
- **Status**: running | complete
```

## Run Orchestration

1. **Resolve variants** — create worktrees / start servers as needed for
   path/branch sources
2. **Select personas** — pick N from `.shakeout/personas.md`
3. **Create directories** — full output structure under `.shakeout/ab/<test-name>/`
4. **Write manifest** — status: running
5. **Launch 2N blind agents in parallel** — each `shakeout-blind` agent receives:
   - Its persona (name + full description)
   - Its variant's URL
   - Its output directory path
6. **Wait for all agents to complete**
7. **Update manifest** — status: complete
8. **Launch synthesis agent** — `shakeout-ab-verdict`

## Blind Agent Changes

The `shakeout-blind` agent currently writes to `.shakeout/`. In A/B mode, the
output directory is passed as part of the launch prompt:

```
The app is running at http://localhost:3001.
Write all output to .shakeout/ab/onboarding-redesign/new-onboarding/marcus-1/.

Your persona:
## Marcus — The Reluctant Sophomore
<full persona description>

Navigate to the app URL and start exploring.
```

No changes to the agent's tool restrictions or cycle — only the output path and
URL vary.

## Synthesis Agent: shakeout-ab-verdict

A new agent that reads all run output and produces the verdict.

### Inputs

- The full `.shakeout/ab/<test-name>/` directory (manifest + all run output)
- Resolved spec files from `.shakeout/config.md` (for grounding)

### Tools

Full Read/Grep/Glob access — it needs to read all output files and spec files.

### Output: verdict.md

```markdown
# A/B Verdict: onboarding-redesign

## Recommendation

**Ship with caveats.** The new onboarding flow significantly improved
discoverability for first-time users (Marcus, Jade) but introduced a
regression in keyboard navigation that blocked DeShawn entirely.
Fix the focus management issue before rolling out.

## Scorecard

| Persona | Metric | main | new-onboarding | Delta |
|---------|--------|------|----------------|-------|
| Marcus | Specs discovered | 8 | 14 | +6 |
| Marcus | Frustrations | 5 | 2 | -3 |
| Marcus | Delights | 1 | 4 | +3 |
| ... | ... | ... | ... | ... |
| **Total** | Specs discovered | 28 | 35 | **+7** |
| **Total** | Frustrations | 12 | 9 | **-3** |
| **Total** | Delights | 5 | 10 | **+5** |

## Regressions

### Focus trap in onboarding modal (Severity: High)
- **Personas affected**: DeShawn (run 3)
- **What happened**: The new onboarding modal has no keyboard escape route.
  DeShawn was trapped and had to refresh the page.
- **Evidence**: "Anxiety — I pressed Escape, Tab, everything. Nothing works.
  I'd close this app and never come back." (reactions.md, DeShawn, variant B)
- **Spec reference**: No accessibility spec exists for the modal (spec gap)

## Improvements

### Search discoverability (Severity: Medium)
- **Personas affected**: Marcus (1), Priya (2)
- **What happened**: ...

## Unchanged

### Coach behavior
Both variants showed identical coach interaction patterns...

## Per-Persona Paired Analysis

### Marcus (Run 1)
**On main**: ...
**On new-onboarding**: ...
**What changed**: ...

### Priya (Run 2)
...
```

## Plugin Changes

| Component | Change |
|-----------|--------|
| `commands/shakeout.md` | Add `--ab`, variant parsing, orchestration steps |
| `agents/shakeout-blind.md` | Accept custom output directory in launch prompt |
| `agents/shakeout-ab-verdict.md` | **New** — synthesis agent |
| `skills/shakeout/SKILL.md` | Document A/B mode, directory structure, verdict agent |
| `README.md` | Add A/B usage examples and output docs |

No changes to `shakeout-compare` (single blind mode), guided cycle, or persona
template.
