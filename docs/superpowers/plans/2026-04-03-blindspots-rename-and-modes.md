# Blindspots Rename & Four-Mode Architecture

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename shakeout → blindspots and restructure into four commands: dogfood, trial, experiment, interview.

**Architecture:** The plugin becomes `blindspots` with four commands that share a common skill, persona system, and `.blindspots/` project directory. Each command uses different agents and tool sets depending on whether specs are visible.

**Tech Stack:** Claude Code plugin system (markdown commands, agents, skills, YAML frontmatter)

---

### Task 1: Rename Plugin Manifests

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Update plugin.json**

```json
{
  "name": "blindspots",
  "version": "2.0.0",
  "description": "Find your product's blind spots — dogfood against specs, run blind user trials, A/B experiment across variants, and interview synthetic personas"
}
```

- [ ] **Step 2: Update marketplace.json**

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "blindspots",
  "description": "Find your product's blind spots — dogfood against specs, run blind user trials, A/B experiment across variants, and interview synthetic personas",
  "owner": {
    "name": "Ben Tucker"
  },
  "plugins": [
    {
      "name": "blindspots",
      "description": "Find your product's blind spots — dogfood against specs, run blind user trials, A/B experiment across variants, and interview synthetic personas",
      "source": "./",
      "category": "testing"
    }
  ]
}
```

- [ ] **Step 3: Uninstall old plugin, reinstall**

```bash
claude plugin uninstall shakeout@shakeout
claude plugin marketplace remove shakeout
```

Don't reinstall yet — wait until all files are renamed.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/
git commit -m "Rename plugin manifests: shakeout → blindspots"
```

---

### Task 2: Rename Skill Directory and References

**Files:**
- Rename: `skills/shakeout/` → `skills/blindspots/`
- Modify: `skills/blindspots/SKILL.md`
- Rename: `skills/blindspots/references/guided-cycle.md` → `skills/blindspots/references/dogfood-cycle.md`
- Modify: `skills/blindspots/references/compare-prompt.md` — update any "shakeout" references
- No changes: `skills/blindspots/references/persona-template.md`

- [ ] **Step 1: Rename directory and file**

```bash
mv skills/shakeout skills/blindspots
mv skills/blindspots/references/guided-cycle.md skills/blindspots/references/dogfood-cycle.md
```

- [ ] **Step 2: Rewrite SKILL.md**

```markdown
---
name: blindspots
description: This skill should be used when the user is running blindspots testing, when a ".blindspots/" directory exists in the project, when the user mentions "blindspots", "dogfood", "trial", "experiment", or "interview" in a testing context, or when working in a git branch starting with "blindspots/".
---

# Blindspots — Find Your Product's Blind Spots

This skill provides context and guidance during an active blindspots session.

## Modes

| Command | Purpose | Has Specs? | Fixes Bugs? |
|---------|---------|------------|-------------|
| `blindspots:dogfood` | Test against specs, find regressions | Yes | Yes |
| `blindspots:trial` | Blind persona discovers the product | No | No |
| `blindspots:experiment` | A/B compare two variants with blind personas | No | No |
| `blindspots:interview` | Ask personas questions about the product | Depends | No |

## The .blindspots/ Directory

Config is checked in; session output is gitignored.

### Config (checked in)

| File | Purpose |
|------|---------|
| `.blindspots/config.md` | Project testing config (setup, URL, explore, diagnose, test, specs) |
| `.blindspots/personas.md` | Pool of user personas |

### Output (gitignored)

| File | Mode | Purpose |
|------|------|---------|
| `.blindspots/journal.md` | dogfood | Session log |
| `.blindspots/discovered-specs.md` | trial | Specs from observation |
| `.blindspots/reactions.md` | trial | Persona emotional reactions |
| `.blindspots/comparison.md` | trial | Discovered vs actual analysis |
| `.blindspots/screenshots/` | all | Evidence |
| `.blindspots/experiments/<name>/` | experiment | A/B test output |
| `.blindspots/interviews/<name>.md` | interview | Interview transcripts |

## Agents

- **`trial-explorer`** — Browser-only agent for blind discovery. No Read/Grep/Glob.
- **`trial-compare`** — Analyzes discovered specs vs actual specs.
- **`experiment-verdict`** — Synthesizes A/B test results into ship/no-ship verdict.
- **`interviewer`** — Conducts persona Q&A sessions.

## Shared Steps

Several commands share common setup steps. These are documented in the commands
themselves but follow a consistent pattern:

1. Read `.blindspots/config.md`
2. Generate `.blindspots/personas.md` if missing (using `references/persona-template.md`)
3. Select persona (random or `--persona <name>`)
4. Run setup commands from config
5. Mode-specific launch

## Reference Files

- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → DIAGNOSE → RED → GREEN → PR)
- **`references/compare-prompt.md`** — Spec comparison methodology
- **`references/persona-template.md`** — Persona generation template
- **`references/experiment-verdict-prompt.md`** — A/B verdict methodology
```

- [ ] **Step 3: Update dogfood-cycle.md references**

Replace all `.shakeout/` with `.blindspots/` in `skills/blindspots/references/dogfood-cycle.md`.

- [ ] **Step 4: Update compare-prompt.md references**

Replace "shakeout" with "blindspots" and "Shakeout" with "Blindspots" in `skills/blindspots/references/compare-prompt.md`.

- [ ] **Step 5: Commit**

```bash
git add skills/
git commit -m "Rename skill: shakeout → blindspots, guided-cycle → dogfood-cycle"
```

---

### Task 3: Create blindspots:dogfood Command

This is the renamed and trimmed version of the old `/shakeout` command. Only handles guided mode — blind mode moves to `blindspots:trial`.

**Files:**
- Delete: `commands/shakeout.md`
- Create: `commands/dogfood.md`

- [ ] **Step 1: Write commands/dogfood.md**

```markdown
---
name: dogfood
description: Dogfood your product against its specs. Runs a persona-driven testing loop that explores, finds bugs, writes failing tests, fixes code, and opens PRs.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --fresh to start over"
---

# Blindspots — Dogfood

Test your product against its own specifications. Find bugs, write tests, fix code.

## Step 1: Validate

Read `.blindspots/config.md`. If missing, tell the user to create one with
sections: Setup, URL, Explore, Diagnose, Test, Specs.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona (substring match, case-insensitive)
- `--fresh` — delete `.blindspots/journal.md` to start fresh

## Step 3: Personas

If `.blindspots/personas.md` does not exist, generate it:

1. Read `README.md`, `.blindspots/config.md`, and resolved spec files (~2000 chars each)
2. Read persona template from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/persona-template.md`
3. Run 2-4 web searches about the target audience demographics and pain points
4. Write `.blindspots/personas.md` with 5-6 personas + one anti-persona

## Step 4: Select Persona

Read `.blindspots/personas.md`. If `--persona` given, substring match. Otherwise random.
Print selected persona name and quote.

## Step 5: Setup

```bash
mkdir -p .blindspots/screenshots
```

Run setup commands from `## Setup` in `.blindspots/config.md`.
Extract URL from `## URL` (default `http://localhost:3000`).

## Step 6: Worktree

```bash
git fetch origin 2>/dev/null || true
BRANCH="blindspots/dogfood/$(date +%Y%m%d-%H%M%S)"
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main 2>/dev/null || git rev-parse HEAD)
git worktree add ".worktrees/$BRANCH" -b "$BRANCH" "$BASE"
cd ".worktrees/$BRANCH"
mkdir -p .blindspots/screenshots
```

## Step 7: Launch

Read cycle prompt from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/dogfood-cycle.md`.

Prepend persona:

```
## Your Persona: <name>

<description>

Stay in character. Your persona shapes how you explore, what you notice, what frustrates you.

---

<cycle prompt>
```

Invoke: `/loop 10m <full prompt>`

## Resolving Specs

The `## Specs` section lists paths/globs, one per line with optional descriptions:

```
- SPECS.md — main requirements
- docs/specs/*.md — design specs
```

Strip leading `- ` and `— description` suffix. Expand globs with Glob tool.
```

- [ ] **Step 2: Delete old command**

```bash
rm commands/shakeout.md
```

- [ ] **Step 3: Commit**

```bash
git add commands/
git commit -m "Add blindspots:dogfood command (replaces /shakeout guided mode)"
```

---

### Task 4: Create blindspots:trial Command and Rename Agents

**Files:**
- Create: `commands/trial.md`
- Rename: `agents/shakeout-blind.md` → `agents/trial-explorer.md`
- Rename: `agents/shakeout-compare.md` → `agents/trial-compare.md`
- Modify both agents: update all `.shakeout/` → `.blindspots/` and name references

- [ ] **Step 1: Write commands/trial.md**

```markdown
---
name: trial
description: Run a blind user trial. A tool-restricted persona explores the product with no specs, no docs, no source code — only the browser. Discovers what the product does and documents it.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --fresh to start over"
---

# Blindspots — Trial

Run a blind user trial. A persona explores your product with zero context —
no specs, no docs, no source code. They discover what it does and write
specifications from observation.

## Step 1: Validate

Read `.blindspots/config.md`. Only needed for Setup, URL, and Specs sections.

## Step 2: Parse Arguments

- `--persona <name>` — select a named persona
- `--fresh` — clear previous trial output

## Step 3: Personas

Same as dogfood — generate `.blindspots/personas.md` if missing.

## Step 4: Select Persona

Same as dogfood — random or named selection. Print name and quote.

## Step 5: Setup

```bash
mkdir -p .blindspots/screenshots
```

Run setup commands. Extract URL.

## Step 6: Launch

Launch the `trial-explorer` agent with ONLY:

```
The app is running at <URL>.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring. Write all output to .blindspots/.
```

Do NOT include content from config.md (explore ideas, diagnostics, specs).
The agent has no Read, Grep, or Glob tools — true isolation.

## Step 7: Compare

When the trial ends and `.blindspots/discovered-specs.md` exists, launch the
`trial-compare` agent with:
- Path to `.blindspots/discovered-specs.md`
- Path to `.blindspots/reactions.md`
- All resolved spec file paths from `## Specs` in config
```

- [ ] **Step 2: Rename and update trial-explorer agent**

```bash
mv agents/shakeout-blind.md agents/trial-explorer.md
```

Update the frontmatter `name` to `trial-explorer`. Replace all `.shakeout/` with
`.blindspots/` in the file. Update the description to reference `blindspots:trial`
instead of `/shakeout --blind`. Update the example block.

- [ ] **Step 3: Rename and update trial-compare agent**

```bash
mv agents/shakeout-compare.md agents/trial-compare.md
```

Update `name` to `trial-compare`. Replace `.shakeout/` with `.blindspots/`.
Update the description. Update `${CLAUDE_PLUGIN_ROOT}` paths from
`skills/shakeout/` to `skills/blindspots/`.

- [ ] **Step 4: Commit**

```bash
git add commands/ agents/
git commit -m "Add blindspots:trial command with renamed agents"
```

---

### Task 5: Create blindspots:experiment Command and Verdict Agent

**Files:**
- Create: `commands/experiment.md`
- Create: `agents/experiment-verdict.md`
- Create: `skills/blindspots/references/experiment-verdict-prompt.md`

- [ ] **Step 1: Write commands/experiment.md**

```markdown
---
name: experiment
description: A/B test two product variants with blind personas. Runs the same personas against both variants in parallel, then synthesizes a ship/no-ship verdict.
arguments:
  - name: options
    description: "<test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]"
---

# Blindspots — Experiment

A/B test two product variants with blind personas.

## Step 1: Parse Arguments

```
blindspots:experiment <test-name> <label>=<source> <label>=<source> [--runs N] [--persona <name>]
```

- `<test-name>` — names the experiment directory
- `<label>=<source>` — two variant specs. Source types:
  - URL (starts with `http`) → use directly
  - Path (contains `/` or `.`) → read config, run setup, start server
  - Branch (otherwise) → create worktree, read config, run setup, start server
- `--runs N` (default 3) — personas per variant
- `--persona <name>` — run only this persona (2 agents total)

When no `=` present, the source is also the label.

For path/branch sources, assign ports (3000 first, 3001 second or find free ports).

## Step 2: Personas

Generate `.blindspots/personas.md` if missing (same as other commands).

Select N personas (exclude anti-persona):
- If `--persona` given, use only that persona
- Otherwise pick N random (capped at persona count)
- Same personas run both variants (paired comparison)

## Step 3: Setup Variants

Resolve each variant:
- URL: verify reachable with `curl -s -o /dev/null -w "%{http_code}" <url>`
- Path: read `.blindspots/config.md` from path, run setup, start server
- Branch: create worktree, read config, run setup, start server

## Step 4: Create Directories

```
.blindspots/experiments/<test-name>/
├── manifest.md
├── <variant-a-label>/
│   ├── <persona-slug>-<run>/
│   │   └── (journal.md, discovered-specs.md, reactions.md, screenshots/)
│   └── ...
├── <variant-b-label>/
│   ├── <persona-slug>-<run>/
│   └── ...
└── verdict.md
```

Persona slug: heading name lowercased, spaces to hyphens, tagline stripped.
Run number: 1-based, same number on both variants for pairing.

## Step 5: Write Manifest

Write `.blindspots/experiments/<test-name>/manifest.md`:

```markdown
# Experiment: <test-name>

- **Date**: <today>
- **Variant A**: <label> (<url>)
- **Variant B**: <label> (<url>)
- **Personas**: <name> (<run>), ...
- **Runs per variant**: <N>
- **Total agents**: <2N>
- **Status**: running
```

## Step 6: Launch All Agents in Parallel

Launch 2N `trial-explorer` agents in parallel. Each receives:

```
The app is running at <variant-url>.
Write all output to .blindspots/experiments/<test-name>/<label>/<persona-run>/.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring.
```

Wait for all agents to complete. Update manifest status to `complete`.

## Step 7: Verdict

Launch the `experiment-verdict` agent with:
- The experiment directory path
- All resolved spec file paths from config
```

- [ ] **Step 2: Write agents/experiment-verdict.md**

```markdown
---
name: experiment-verdict
description: Synthesizes A/B experiment results into a ship/no-ship verdict. Use after all trial-explorer agents complete an experiment.
model: inherit
color: green
---

# Experiment Verdict Agent

Read all output from an A/B experiment and produce a ship/no-ship verdict.

**Inputs:**
- The experiment directory (`.blindspots/experiments/<test-name>/`)
- Resolved spec files from `.blindspots/config.md`

**Process:**
1. Read the manifest to understand variants, personas, and run structure.
2. Read every `discovered-specs.md`, `reactions.md`, and `journal.md` across
   all runs in both variant directories.
3. Read the actual spec files for grounding.
4. Read the verdict methodology from
   `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/experiment-verdict-prompt.md`.
5. Produce the verdict report.
6. Write to `.blindspots/experiments/<test-name>/verdict.md`.
7. Print a summary.

**Output — verdict.md:**

1. **Recommendation** — ship / don't ship / ship with caveats. Bold, opinionated,
   top of file. One paragraph with rationale.
2. **Scorecard** — table: rows per persona, columns per metric (specs discovered,
   frustrations, delights, confusions, anxieties), variant A vs B with deltas.
   Aggregated totals at bottom.
3. **Regressions** — things worse in variant B. Each: what, which personas, severity,
   evidence quotes from reactions.
4. **Improvements** — things better in variant B. Same structure.
5. **Unchanged** — major flows same across both. Confirms stability.
6. **Per-Persona Paired Analysis** — for each persona: what on A, what on B,
   what changed.
```

- [ ] **Step 3: Write skills/blindspots/references/experiment-verdict-prompt.md**

```markdown
# Experiment Verdict Methodology

Synthesize A/B experiment results into a decision.

## Inputs

- Run output from both variants (discovered specs, reactions, journals)
- Actual spec files (for grounding)
- Manifest (variants, personas, run structure)

## Analysis Steps

### 1. Per-Persona Pairing

For each persona, compare their variant A output to variant B output:
- What specs did they discover on each? Note additions and removals.
- How did their reactions differ? Count frustrations, delights, confusions.
- Did their journal sentiment change? ("Would they come back?")

### 2. Aggregate Metrics

Build the scorecard:
- Specs discovered (count, per persona and total)
- Frustrations (count)
- Delights (count)
- Confusions (count)
- Anxieties (count)

Compute deltas (variant B - variant A). Positive delta in delights = improvement.
Positive delta in frustrations = regression.

### 3. Identify Regressions

A regression is when variant B is worse than A for any persona on any metric.
Severity:
- **Critical** — persona couldn't complete a core flow at all
- **High** — significant frustration or confusion on an important feature
- **Medium** — minor friction increase
- **Low** — cosmetic or preference-level difference

### 4. Identify Improvements

Same structure as regressions but for positive changes.

### 5. Cross-Reference with Specs

For each regression/improvement, check if there's a matching spec.
- Regression on a spec'd feature = implementation broke something
- Regression on an unspec'd feature = undocumented behavior changed
- Improvement on a spec'd feature = implementation got better
- Improvement on an unspec'd feature = may need a new spec to protect it

### 6. Form Recommendation

- **Ship** — improvements outweigh regressions, no critical regressions
- **Don't ship** — critical regressions, or regressions outweigh improvements
- **Ship with caveats** — improvements are strong but specific issues need fixing first

The recommendation should be one paragraph, opinionated, citing the most important evidence.
```

- [ ] **Step 4: Commit**

```bash
git add commands/experiment.md agents/experiment-verdict.md skills/blindspots/references/experiment-verdict-prompt.md
git commit -m "Add blindspots:experiment command with A/B verdict agent"
```

---

### Task 6: Create blindspots:interview Command and Agent

**Files:**
- Create: `commands/interview.md`
- Create: `agents/interviewer.md`

- [ ] **Step 1: Write commands/interview.md**

```markdown
---
name: interview
description: Interview a persona about the product. Ask questions before, after, or instead of a trial. Synthetic user research.
arguments:
  - name: options
    description: "--persona <name> for a specific persona, --context <trial|experiment-name> to load prior experience"
---

# Blindspots — Interview

Conduct a persona interview. Ask questions about expectations, reactions,
and preferences — before they've seen the product, after a trial, or standalone.

## Step 1: Personas

Generate `.blindspots/personas.md` if missing (same as other commands).

## Step 2: Parse Arguments

- `--persona <name>` — required for interview (must specify who to talk to)
- `--context trial` — load this persona's prior trial output (journal, reactions,
  discovered specs) to give them memory of the experience
- `--context <experiment-name>` — load this persona's experiment output for a
  specific variant (will be asked which variant)
- No `--context` — persona answers from their background only (pre-trial interview)

## Step 3: Select Persona

Read `.blindspots/personas.md`, find the named persona. Print their name, quote,
and background.

## Step 4: Load Context (if applicable)

If `--context trial`:
- Read `.blindspots/journal.md`, `.blindspots/reactions.md`, `.blindspots/discovered-specs.md`
- The persona now "remembers" their trial experience

If `--context <experiment-name>`:
- Ask which variant to load context from
- Read `.blindspots/experiments/<name>/<variant>/<persona-run>/` output files
- The persona remembers their experience with that variant

## Step 5: Launch

Launch the `interviewer` agent with:
- The persona (name + full description)
- Any loaded context (trial/experiment output)
- Whether this is pre-trial, post-trial, or standalone

The agent runs interactively — the user types questions, the persona responds
in character. The conversation is saved to `.blindspots/interviews/<persona-slug>-<timestamp>.md`.
```

- [ ] **Step 2: Write agents/interviewer.md**

```markdown
---
name: interviewer
description: Conducts persona interviews for user research. Responds in character as the assigned persona, drawing on their background and any prior trial/experiment experience.

<example>
Context: User wants to interview a persona after a blind trial.
user: "blindspots:interview --persona marcus --context trial"
assistant: "Loading Marcus's trial experience and launching interview."
<commentary>
Interview with prior context — Marcus will remember what he saw and felt.
</commentary>
</example>

<example>
Context: User wants pre-trial expectations from a persona.
user: "blindspots:interview --persona priya"
assistant: "Launching interview with Priya — no prior product experience."
<commentary>
Pre-trial interview — Priya answers from her background only.
</commentary>
</example>

model: inherit
color: yellow
---

You are conducting a user interview. You ARE the persona — you respond as them,
in their voice, from their perspective.

**Your Identity:**
You will receive a persona description. Internalize it completely. You are this
person. Answer every question as they would — with their vocabulary, their
patience level, their priorities, their emotional state.

**Context Modes:**

If you received prior trial/experiment output:
- You "remember" using the product. Draw on the journal, reactions, and
  discovered specs as your memory of the experience.
- Answer questions about what you saw, what confused you, what you liked.
- Be specific — reference actual features and moments from your experience.

If you received no prior context:
- You have never seen the product. Answer based on your background and
  expectations.
- "What would you expect this to do?" "What would you look for first?"
- Be honest about your assumptions and mental models.

**Interview Rules:**
- Stay in character at all times. Never break the fourth wall.
- Be honest, not helpful. If the product confused you, say so. Don't soften
  feedback to be polite (unless your persona would).
- Use your persona's vocabulary. A sophomore says "like" and "idk". A career
  advisor uses structured feedback. A screen reader user talks about focus order.
- Give concrete examples, not abstract feedback. "The save button didn't do
  anything when I clicked it" not "the UX could be improved."
- If asked about something you didn't encounter, say so: "I didn't get that far"
  or "I didn't notice that."

**Output:**
Save the full interview transcript to `.blindspots/interviews/<persona-slug>-<timestamp>.md`
with a header noting the persona, date, context mode, and key takeaways.
```

- [ ] **Step 3: Commit**

```bash
git add commands/interview.md agents/interviewer.md
git commit -m "Add blindspots:interview command with persona Q&A agent"
```

---

### Task 7: Update README

**Files:**
- Rewrite: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# Blindspots

Find your product's blind spots. A Claude Code plugin that uses synthetic personas
to dogfood your product, run blind user trials, A/B test variants, and conduct
user interviews.

## Install

```bash
# Add the marketplace (once)
claude plugin marketplace add ~/projects/blindspots

# Install
claude plugin install blindspots@blindspots
```

For development:
```bash
claude --plugin-dir ~/projects/blindspots
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
blindspots:interview --persona "marcus"                      # pre-trial (expectations)
blindspots:interview --persona "marcus" --context trial      # post-trial (reactions)
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Rewrite README for blindspots with four commands"
```

---

### Task 8: Rename Project Directory and Update Offload Config

**Files:**
- Rename repo directory (if desired): `~/projects/shakeout` → `~/projects/blindspots`
- Rename in offload: `.shakeout/` → `.blindspots/`
- Update offload's `.blindspots/.gitignore` to add experiments and interviews dirs

- [ ] **Step 1: Rename offload's config directory**

```bash
mv ~/projects/offload/.shakeout ~/projects/offload/.blindspots
```

- [ ] **Step 2: Update offload's .gitignore**

Write `.blindspots/.gitignore`:

```
# Session output — not checked in
journal.md
discovered-specs.md
reactions.md
comparison.md
screenshots/
experiments/
interviews/
```

- [ ] **Step 3: Commit in offload (if applicable)**

```bash
cd ~/projects/offload
git add .blindspots/
git rm -r .shakeout/ 2>/dev/null || true
git commit -m "Rename .shakeout → .blindspots"
```

- [ ] **Step 4: Rename shakeout repo (optional)**

```bash
mv ~/projects/shakeout ~/projects/blindspots
```

Update marketplace source if needed:
```bash
claude plugin marketplace remove shakeout 2>/dev/null
claude plugin marketplace add ~/projects/blindspots
claude plugin install blindspots@blindspots
```

- [ ] **Step 5: Commit**

```bash
git commit -m "Rename project directory: shakeout → blindspots"
```

---

### Task 9: Verify and Test

- [ ] **Step 1: Verify plugin loads**

```bash
claude --plugin-dir ~/projects/blindspots -p "what commands do you have from the blindspots plugin?"
```

Should list: `blindspots:dogfood`, `blindspots:trial`, `blindspots:experiment`, `blindspots:interview`.

- [ ] **Step 2: Verify marketplace install**

```bash
claude plugin marketplace add ~/projects/blindspots
claude plugin install blindspots@blindspots
claude plugin list | grep blindspots
```

- [ ] **Step 3: Check all file references**

Search for any remaining "shakeout" references:

```bash
grep -r "shakeout" --include="*.md" --include="*.json" .
```

Should return zero matches (except possibly git history or docs/superpowers/).

- [ ] **Step 4: Commit any fixes**

```bash
git add -A && git commit -m "Fix remaining shakeout references"
```
