---
name: setup
description: Set up blindspots for your project. Generates .blindspots/config.md and .blindspots/personas.md interactively.
arguments:
  - name: options
    description: "--fresh to regenerate from scratch"
---

# Blindspots — Setup

Generate project config and personas interactively.

## Step 1: Check Existing

If `.blindspots/config.md` exists and `--fresh` not given, ask user if they want to regenerate or keep existing.

## Step 2: Read Project Context

Read available project files to understand the product:
- `README.md`
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or equivalent
- Any existing docs (check `docs/` directory)
- `.blindspots/config.md` if it exists (for reference)

## Step 3: Ask Clarifying Questions

Ask one question at a time to fill in the config:

1. **Product type** — "What kind of product is this? (webapp, CLI tool, Claude Code plugin, API, other)"
2. **Setup commands** — "How do you start the product for development?" Suggest based on what was found (e.g. "I see a `dev` script in package.json — is `npm run dev` how you start it?")
3. **Start instructions** — "How would a new user begin using it?" For a webapp, this is the URL. For a CLI, the command. For a plugin, reading the README.
4. **Specs** — "Do you have specification or requirements files?" Suggest any found (e.g. "I found `SPECS.md` and files in `docs/specs/`")
5. **Explore** (optional) — "Any specific features or flows you'd like personas to focus on?"
6. **Diagnose** (optional) — "Where should personas look when things break? (logs, console, specific files)"
7. **Test** (optional) — "What's your test framework and how do you run tests?"

Skip questions where the answer is obvious from context. Don't ask about optional sections unless the user seems interested.

## Step 4: Write Config

```bash
mkdir -p .blindspots
```

Write `.blindspots/config.md` with the gathered information. Use `## Start` (not `## URL`). Include only sections that have content.

## Step 5: Generate Personas

1. Read `README.md`, `.blindspots/config.md`, and resolved spec files (~2000 chars each)
2. Read persona template from `${CLAUDE_PLUGIN_ROOT}/skills/blindspots/references/persona-template.md`
3. Run 2-4 web searches about the target audience demographics and pain points
4. Generate 5-6 persona candidates + one anti-persona

## Step 5b: Validate Diversity

Check the generated personas against the diversity checklist from the template.
Print the checklist with each item marked as covered or missing, and which
persona satisfies it:

```
Diversity check:
  ✓ Accessibility needs — <persona name> (screen reader)
  ✗ Mobile-primary user — no persona covers this
  ✓ Poor connectivity — <persona name> (2G, old Android)
  ...
```

If any required items are uncovered, adjust an existing persona or generate an
additional one to fill the gap before presenting to the user. The goal is to
present a set that already satisfies the checklist — not to hope the user
notices gaps.

## Step 6: Present Personas

Present each persona to the user one at a time:
- Name, background, quote, goals, behavior patterns
- Ask: "Does this feel like one of your users? Anything you'd change?"
- User can tweak, drop, or approve each one

## Step 7: Write Personas

Write `.blindspots/personas.md` with the approved set.

## Step 8: Summary

Print what was generated:
- Config file location and key settings
- Number of personas and their names
- Suggest next step: "Run `/dogfood` to start testing"
