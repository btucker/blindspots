---
name: shakeout
description: Start an exploratory testing session. Uses the product as a real user to find bugs, write failing tests, fix code, and open PRs.
arguments:
  - name: options
    description: "--blind for discovery mode (no specs), --persona <name> for a specific persona, --fresh to start over"
---

# Shakeout — Exploratory Testing

Launch an autonomous exploratory testing loop for the current project.

## Step 1: Validate Project

Read `.shakeout/config.md` from the project. If it does not exist, stop and tell
the user to create one (explain the required sections: Setup, URL, Explore,
Diagnose, Test). Save the contents for later use.

## Step 2: Parse Arguments

Parse the arguments provided after `/shakeout`:
- `--blind` — blind discovery mode (no specs, no docs)
- `--persona <name>` — select a named persona (substring match, case-insensitive)
- `--fresh` — delete `.shakeout/journal.md` to start a fresh session

If no arguments are provided, run in guided mode with a random persona.

## Step 3: Generate Personas

Check if `.shakeout/personas.md` exists. If it does NOT exist, generate it using
the template in `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/persona-template.md`.

1. Read the project's `README.md` and `.shakeout/config.md`
2. Resolve the spec sources from the `## Specs` section (see "Resolving Specs" below)
   and read the first ~2000 chars of each resolved file for context
3. Read the persona template from the reference file
3. **Research the target audience.** Use web searches to ground personas in real data:
   - Search for the product's user demographic (e.g., "college student internship
     search behavior 2025", "first-generation college student career planning challenges")
   - Search for accessibility and device usage patterns in the target demographic
     (e.g., "college student mobile vs desktop usage", "screen reader usage among students")
   - Search for common pain points and goals (e.g., "why students abandon career tools",
     "what college students want from job search apps")
   - Use 2-4 targeted searches — enough to inform the personas, not exhaustive research
4. Write `.shakeout/personas.md` with 5-6 personas (plus one anti-persona) following
   the template structure. Incorporate the research findings into quantified pain
   points and realistic behavior patterns. Each persona must be specific to THIS product.
5. Tell the user the personas were generated and summarize what research informed them

## Step 4: Select Persona

Read `.shakeout/personas.md` and select a persona:
- If `--persona <name>` was given, find the first persona whose heading contains
  the substring (case-insensitive). If not found, list available personas and stop.
- Otherwise, pick one at random.

Print the selected persona name and their quote.

## Step 5: Setup

Create the `.shakeout/` output directories if they don't exist:

```bash
mkdir -p .shakeout/screenshots
```

Check if the project's dev server needs to be started by running the command in
the `## Setup` section of `.shakeout/config.md` (the fenced code block under that
heading). Extract the URL from the `## URL` section (default to `http://localhost:3000`).

## Step 6: Enter Worktree

Create an isolated git worktree for this shakeout session:

```bash
git fetch origin 2>/dev/null || true
BRANCH="shakeout/$(date +%Y%m%d-%H%M%S)"
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main 2>/dev/null || git rev-parse HEAD)
git worktree add ".worktrees/$BRANCH" -b "$BRANCH" "$BASE"
cd ".worktrees/$BRANCH"
mkdir -p .shakeout/screenshots
```

## Step 7: Launch

### Guided Mode

Read the cycle prompt from `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/guided-cycle.md`.

Construct the full loop prompt by prepending the persona:

```
## Your Persona: <selected persona name>

<persona description>

Stay in character throughout the session. Your persona shapes how you explore,
what you notice, and what frustrates you.

---

<cycle prompt content>
```

Then invoke: `/loop 10m <full prompt>`

### Blind Mode

Launch the `shakeout-blind` agent with a prompt containing ONLY:

```
The app is running at <URL>.

Your persona:
## <persona name>
<full persona description>

Navigate to the app URL and start exploring. Write all output to .shakeout/.
```

Do NOT include any content from `.shakeout/config.md` (explore ideas, diagnostics,
specs, references). The blind agent must discover everything through the browser.

The blind agent has **no Read, Grep, or Glob tools** — it can only interact
through the browser and write output to `.shakeout/`. This enforces true
isolation from specs and source code.

## Step 8: After Blind Mode

When a blind shakeout ends and `.shakeout/discovered-specs.md` exists, launch
the `shakeout-compare` agent to compare discovered specs against the actual specs.
Pass it:
- The path to `.shakeout/discovered-specs.md`
- The path to `.shakeout/reactions.md`
- All resolved spec file paths (from `## Specs` in `.shakeout/config.md`)

The comparison report will be written to `.shakeout/comparison.md`.

## Resolving Specs

The `## Specs` section in `.shakeout/config.md` lists spec sources, one per line.
Each line has a path (or glob) and an optional `—` description:

```
- SPECS.md — main requirements
- docs/specs/*.md — design specs
- docs/plans/*.md — implementation plans
```

To resolve:
1. Strip the leading `- ` and any `— description` suffix from each line
2. Trim whitespace to get the raw path/glob
3. Use the Glob tool to expand patterns (e.g., `docs/specs/*.md` → list of files)
4. Plain file paths resolve directly

The resolved list of files is used for:
- **Persona generation** (Step 3) — read first ~2000 chars of each for context
- **Comparison** (Step 8) — pass all paths to the compare agent
