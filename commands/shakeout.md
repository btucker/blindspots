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

Read `SHAKEOUT.md` from the project root. If it does not exist, stop and tell the
user to create one (explain the required sections: Setup, URL, Explore, Diagnose,
Test). Save the contents for later use.

## Step 2: Parse Arguments

Parse the arguments provided after `/shakeout`:
- `--blind` — blind discovery mode (no specs, no docs)
- `--persona <name>` — select a named persona (substring match, case-insensitive)
- `--fresh` — delete `shakeout-journal.md` to start a fresh session

If no arguments are provided, run in guided mode with a random persona.

## Step 3: Generate Personas

Check if `SHAKEOUT-PERSONAS.md` exists in the project root. If it does NOT exist,
generate it using the template in `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/persona-template.md`.

1. Read the project's `README.md`, `SHAKEOUT.md`, and any file referenced in the
   `## Specs` section of `SHAKEOUT.md` (first 8000 chars of specs)
2. Read the persona template from the reference file
3. **Research the target audience.** Use web searches to ground personas in real data:
   - Search for the product's user demographic (e.g., "college student internship
     search behavior 2025", "first-generation college student career planning challenges")
   - Search for accessibility and device usage patterns in the target demographic
     (e.g., "college student mobile vs desktop usage", "screen reader usage among students")
   - Search for common pain points and goals (e.g., "why students abandon career tools",
     "what college students want from job search apps")
   - Use 2-4 targeted searches — enough to inform the personas, not exhaustive research
4. Write `SHAKEOUT-PERSONAS.md` with 5-6 personas (plus one anti-persona) following
   the template structure. Incorporate the research findings into quantified pain
   points and realistic behavior patterns. Each persona must be specific to THIS product.
5. Tell the user the personas were generated and summarize what research informed them

## Step 4: Select Persona

Read `SHAKEOUT-PERSONAS.md` and select a persona:
- If `--persona <name>` was given, find the first persona whose heading contains
  the substring (case-insensitive). If not found, list available personas and stop.
- Otherwise, pick one at random.

Print the selected persona name.

## Step 5: Setup

Check if the project's dev server needs to be started by running the command in
the `## Setup` section of `SHAKEOUT.md` (the fenced code block under that heading).
Extract the URL from the `## URL` section (default to `http://localhost:3000`).

## Step 6: Enter Worktree

Create an isolated git worktree for this shakeout session:

```bash
git fetch origin 2>/dev/null || true
BRANCH="shakeout/$(date +%Y%m%d-%H%M%S)"
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main 2>/dev/null || git rev-parse HEAD)
git worktree add ".worktrees/$BRANCH" -b "$BRANCH" "$BASE"
cd ".worktrees/$BRANCH"
```

## Step 7: Start the Loop

Read the appropriate cycle prompt from the plugin's references directory:
- **Guided mode**: Read `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/guided-cycle.md`
- **Blind mode**: Read `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/blind-cycle.md`

Construct the full loop prompt by prepending the persona:

```
## Your Persona: <selected persona name>

<persona description>

Stay in character throughout the session. Your persona shapes how you explore,
what you notice, and what frustrates you.

---

<cycle prompt content>
```

For **blind mode**, also prepend:

```
IMPORTANT: Do NOT read any spec files, design docs, requirements, READMEs, or
AGENTS.md in this project. Discover behavior only through the UI.
```

Then invoke: `/loop 10m <full prompt>`

## Step 8: After Blind Mode (if applicable)

When a blind shakeout ends and `shakeout-discovered-specs.md` exists in the
working directory, launch the `shakeout-compare` agent to compare discovered
specs against the actual specs. Pass it:
- The path to `shakeout-discovered-specs.md`
- The path to the specs file (from `## Specs` in SHAKEOUT.md)
