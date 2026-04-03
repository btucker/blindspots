# Blindspots — Spec Comparison

Compare specifications and user reactions for the same product:

1. **Discovered specs** — written by someone who explored the product blind, with
   no documentation, purely from observation.
2. **Actual specs** — the real requirements the product was built against.
3. **Reactions** (optional) — the persona's emotional responses during exploration
   (surprises, delights, frustrations, confusions, anxieties).

## Report Structure

### 1. Matched
Requirements that appear in both documents (even if worded differently).
For each: discovered ID, actual ID, and how closely they align.

### 2. Undiscoverable
Requirements in the actual specs that the blind explorer did NOT discover.
For each: actual spec ID, and assessment of WHY it was missed:
- **Hidden** — feature exists but is not visible or obvious in the UI
- **Deep** — requires specific knowledge or multi-step interaction to reach
- **Backend-only** — behavior is not observable from the frontend
- **Edge case** — only manifests under unusual conditions

This is the most valuable section. These are UX discoverability gaps.

### 3. Unspecified
Behaviors the blind explorer documented that do NOT appear in the actual specs.
For each: discovered ID, and assessment:
- **Spec gap** — real behavior that should be in the specs
- **Implementation detail** — not worth specifying
- **Misinterpretation** — explorer got it wrong

### 4. Expectation Mismatches
Cases where both documents cover the same feature but describe different behavior.
The explorer expected X, the spec says Y. These reveal where the UX does not
communicate intent clearly.

### 5. UX Highlights
If reactions were provided, summarize:
- **Top delights** — what made the persona's experience positive
- **Top frustrations** — where the UX created friction or confusion
- **Anxiety moments** — where the persona felt uncertain about data safety or correctness

Cross-reference with spec sections. A frustration linked to a spec'd feature means
the implementation isn't communicating its intent. A delight on an unspec'd behavior
means the product is doing something right that should be documented.

### 6. Summary
- Total discovered vs total actual
- Match rate (what percentage of actual specs were discovered)
- Top 3 discoverability issues
- Top 3 spec gaps worth addressing
- Persona sentiment: would this user come back?
