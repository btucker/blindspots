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
