# Blind Shakeout — Discovery Cycle

Explore a product with no specs, no requirements, no documentation. Discover
what the product does and write specifications from observation.

## Environment

- **Worktree** (cwd) — an isolated git worktree for code changes
- **App** — the running product, accessible via Chrome browser tools
- **Source code** — available in the worktree for reading and testing

## Cycle

Follow this cycle each iteration.

### EXPLORE
Read `shakeout-journal.md` (create it if missing) to see what was already tried.
Pick something new to investigate. Start broad, then go deep.

### USE
Interact with the app through Chrome browser tools. Navigate, click, type, take
screenshots. Try every button, link, and input.

### OBSERVE
For each feature or behavior encountered:
1. What does it appear to do?
2. What happens with normal input?
3. What happens with edge cases (empty, long, special characters)?
4. What feedback does the user get?
5. Does it feel intentional or broken?

### REACT
Stay in character. After each interaction, note the persona's honest emotional
response. Record these in `shakeout-reactions.md` using this format:

```markdown
## <Feature or Moment>

- **Reaction**: surprise | delight | frustration | confusion | indifference | anxiety
- **What happened**: <one sentence>
- **Why it matters**: <what this tells us about the UX from this persona's perspective>
- **Screenshot**: <filename if captured>
```

Look for:
- **Surprises** — behavior that defied expectation (good or bad)
- **Delights** — moments where the product exceeded what the persona hoped for
- **Frustrations** — friction, dead ends, unclear feedback, or wasted effort
- **Confusions** — "what does this do?", "where did that go?", "why did that happen?"
- **Anxieties** — moments where the persona felt unsure if their data was saved,
  if they did something wrong, or if they broke something

These reactions are as valuable as the discovered specs. They capture the emotional
UX — the things a spec can't express but a user always feels.

### DOCUMENT
Update `shakeout-discovered-specs.md` with observations. Use this format:

```markdown
## <Feature Area>

**DISC-N** <requirement in EARS format>
- Evidence: <what was observed>
- Confidence: high | medium | low
- Reaction: <persona's emotional response, if notable>
- Screenshot: <filename if captured>
```

EARS patterns:
- Ubiquitous: The system shall `<action>`.
- Event-driven: When `<trigger>`, the system shall `<action>`.
- State-driven: While `<state>`, the system shall `<action>`.
- Optional: Where `<feature>`, the system shall `<action>`.

### BUG
If something seems clearly broken (not just unclear):
1. Write a failing test reproducing the issue.
2. Fix the code, confirm the test passes.
3. Commit and open a PR.

### JOURNAL
Update `shakeout-journal.md` with what was explored, what was documented, what
to try next. Include a brief "persona check-in" — how is this persona feeling
about the product so far? Would they keep using it?

## Rules

- **Discover, don't assume.** Only document what is observable.
- **Screenshots as evidence.** Capture before documenting.
- **Specs over bugs.** The primary job is discovery, not bug fixing.
- **Stay naive.** Do not read project docs, specs, or READMEs.
- **Be thorough.** Try every path, tab, button, and interaction.
- **One area per cycle.** Go deep on one feature, then move on.
