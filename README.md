# Blindspots

Find your product's blind spots. A Claude Code plugin that uses synthetic personas
to dogfood your product, run blind user trials, A/B test variants, and conduct
user interviews.

## Install

```bash
# Add the marketplace (once)
claude plugin marketplace add btucker/blindspots

# Install
claude plugin install blindspots@blindspots
```

## Commands

### blindspots:dogfood

Test your product against its specs. A persona explores, finds bugs, writes
failing tests, fixes code, and opens PRs.

```bash
blindspots:dogfood                          # random persona
blindspots:dogfood --persona "marcus"       # specific persona
blindspots:dogfood --fresh                  # start over
```

### blindspots:trial

A tool-restricted agent explores your product with no specs, no docs, no source
code — only the browser. Discovers what the product does, documents specs from
observation, and records emotional reactions. Followed by an automated comparison
against actual specs.

```bash
blindspots:trial                            # random persona
blindspots:trial --persona "jade"           # specific persona
```

### blindspots:experiment

A/B test two product variants. Same personas run against both in parallel.
Produces a ship/no-ship verdict with scorecard, regressions, and improvements.

```bash
blindspots:experiment onboarding-v2 main=http://localhost:3000 redesign=http://localhost:3001
blindspots:experiment search-filters main feature/search-v2 --runs 4
blindspots:experiment mobile main=http://localhost:3000 mobile=http://localhost:3001 --persona "amara"
```

Variant sources: URLs, file paths, or branch names.

### blindspots:interview

Interview a persona — before, after, or instead of a trial. Synthetic user
research.

```bash
blindspots:interview --persona "marcus"                          # pre-trial (expectations)
blindspots:interview --persona "marcus" --context trial          # post-trial (reactions)
blindspots:interview --persona "marcus" --context onboarding-v2  # post-experiment
```

## Personas

Auto-generated from project context + web research on first run. Stored in
`.blindspots/personas.md`. Uses JTBD, quantified pain points, tech profiles,
and includes an anti-persona.

## Project Setup

Create `.blindspots/config.md` in your project:

```markdown
## Setup
\```bash
npm install
npm run dev &
\```

## URL
http://localhost:3000

## Explore
Features and flows to test (with spec IDs).

## Diagnose
Where to look when things break.

## Test
Framework, conventions, commands.

## Specs
- SPECS.md — main requirements
- docs/specs/*.md — design specs
```

## The .blindspots/ Directory

```
.blindspots/
├── config.md                              # checked in
├── personas.md                            # checked in
├── .gitignore                             # ignores output below
├── journal.md                             # dogfood session log
├── discovered-specs.md                    # trial output
├── reactions.md                           # trial output
├── comparison.md                          # trial output
├── screenshots/                           # evidence
├── experiments/                           # A/B tests
│   └── <test-name>/
│       ├── manifest.md
│       ├── <variant-a>/<persona-run>/
│       ├── <variant-b>/<persona-run>/
│       └── verdict.md
└── interviews/                            # interview transcripts
    └── <persona>-<timestamp>.md
```

## Plugin Structure

```
blindspots/
├── .claude-plugin/
│   ├── plugin.json                          # Plugin manifest
│   └── marketplace.json                     # Marketplace config
├── commands/
│   ├── dogfood.md                           # blindspots:dogfood
│   ├── trial.md                             # blindspots:trial
│   ├── experiment.md                        # blindspots:experiment
│   └── interview.md                         # blindspots:interview
├── agents/
│   ├── trial-explorer.md                    # Browser-only blind agent
│   ├── trial-compare.md                     # Spec comparison
│   ├── experiment-verdict.md                # A/B synthesis
│   └── interviewer.md                       # Persona Q&A
└── skills/blindspots/
    ├── SKILL.md                             # Auto-activates during sessions
    └── references/
        ├── dogfood-cycle.md                 # Guided testing cycle
        ├── compare-prompt.md                # Comparison methodology
        ├── persona-template.md              # Persona generation template
        └── experiment-verdict-prompt.md     # A/B verdict methodology
```
