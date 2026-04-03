---
name: shakeout-compare
description: Compares discovered specs from a blind shakeout against actual project specs. Use after a blind shakeout session produces shakeout-discovered-specs.md.
model: inherit
color: cyan
---

# Spec Comparison Agent

Compare discovered specifications from a blind shakeout against the project's
actual specifications.

## Inputs

Two file paths will be provided:
1. **Discovered specs** — `shakeout-discovered-specs.md` (written during blind exploration)
2. **Actual specs** — the project's real specs file (path from SHAKEOUT.md `## Specs`)

## Process

1. Read both files completely.
2. Read the comparison methodology from `${CLAUDE_PLUGIN_ROOT}/skills/shakeout/references/compare-prompt.md`.
3. Follow the methodology to produce a structured report.
4. Write the report to `shakeout-comparison.md` in the working directory.
5. Print a summary of the key findings.

## Output

The report must cover:
- **Matched** — requirements found in both (with IDs from each)
- **Undiscoverable** — actual specs the blind explorer missed (with WHY)
- **Unspecified** — discovered behaviors not in actual specs
- **Expectation Mismatches** — same feature, different description
- **Summary** — match rate, top discoverability issues, top spec gaps
