# Blindspots

A Claude Code plugin that gives you synthetic users for your product. They
use it like real people would — and find things you might not otherwise notice.

## How it works

You install the plugin, point it at your running app, and type `/dogfood`.

Blindspots reads your project — README, specs, config — and generates a cast of
synthetic personas based on your actual target audience. It picks one, opens a
browser, and starts using your product in character.

From there, four modes let you ask different questions about your product:

### Does it work? `/dogfood`

Your persona tests the product against your specs. When it finds something that
doesn't match — a broken flow, a missing feature, a wrong behavior — it writes a
failing test, fixes the code, and opens a PR. Then it keeps going.

### Can someone actually use this? `/user-trial`

The persona gets no specs, no docs, no source code — just a browser and a URL.
It explores on its own and writes down what it thinks your product does. Then
Blindspots compares those observations against your actual specs. The gaps
between what you built and what they perceived — those are your blind spots.

### Which version is better? `/experiment`

Run trials against two variants of your product in parallel — your main branch
vs. a redesign, v1 vs. v2, localhost:3000 vs. localhost:3001. Same personas,
both versions. Produces a scorecard and a ship/no-ship verdict. Test ideas
without releasing them to real users.

### Why? `/interview`

Talk to a persona directly. Ask what they expected before a user trial, how they
felt after one, or what they think of your onboarding. Synthetic user research, on
demand.

## Install

```bash
claude plugin install blindspots from btucker/blindspots
```

## Setup

Create `.blindspots/config.md` in your project:

```markdown
## Setup
npm run dev &

## URL
http://localhost:3000

## Specs
- SPECS.md
```

That's the minimum. Tell it how to start your app, where it's running, and where
your specs live. Then run `/dogfood`.

### Optional config sections

| Section | Purpose |
|---------|---------|
| `## Explore` | Features and flows to test |
| `## Diagnose` | Where to look when things break |
| `## Test` | Test framework and conventions |

## Personas

Generated automatically on first run from your project context and web research
about your target audience. Saved to `.blindspots/personas.md` — check it in,
edit it, make them yours.

Every command picks a random persona unless you pass `--persona "name"`.
