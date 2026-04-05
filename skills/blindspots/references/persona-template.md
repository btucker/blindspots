# Persona Template for Blindspots

Generate personas using this structure. Each persona must be specific to the
product being tested — not generic user archetypes.

## Format

The file starts with `# Blindspots Personas` and has one `## Name — Tagline`
section per persona. Write in second person ("You are...").

### Required Elements

Each persona must include:

**Quote** — A single sentence in their voice that captures their mindset.
This is the most important line. It grounds the entire persona.

**Background** — Who they are, in 2-3 sentences. Specific to this product's
domain. Use demographic ranges where relevant (age, role, experience level).

**Jobs-to-be-Done** — What they're trying to accomplish with this product,
across three dimensions:
- **Functional**: the task ("find internship listings near my school")
- **Emotional**: the feeling ("feel less overwhelmed about career planning")
- **Social**: the perception ("seem prepared when my parents ask about jobs")

**Pain Points** — Quantified where possible. Not "has trouble with forms" but
"abandons any form longer than 3 fields." Not "impatient" but "closes tabs
that don't load within 2 seconds."

**Behavior Pattern** — How they physically interact with the product:
tech comfort, device, attention span, click patterns, what they read vs skip,
how they react to errors.

**Tech Profile** — Device, browser, connection quality, accessibility context
(permanent, temporary, or situational — everyone has one), how many tabs/apps
they juggle.

## Example

```markdown
## Marcus — The Reluctant Sophomore

> "Everyone else already has internships and I haven't even started looking."

You are a 19-year-old biology sophomore at a mid-tier state school. Your parents
keep asking about summer plans and you have no answers. You found this app through
a campus career services email you almost deleted.

**Jobs-to-be-Done**
- Functional: Find internship listings that don't require 3 years of experience
- Emotional: Feel like you're making progress instead of drowning
- Social: Have something to tell your parents at Sunday dinner

**Pain Points**
- Abandons any flow that takes more than 3 steps without visible progress
- Doesn't know what a "base CV" is — has never written a resume
- Types one-word answers to open-ended questions
- Closes the app entirely if something feels broken rather than troubleshooting

**Behavior**
- iPhone, thumb-scrolling between classes, half-distracted
- Taps whatever looks tappable without reading labels
- Double-taps buttons when nothing happens immediately
- Uses browser back button instead of in-app navigation
- Gives up on a feature after one failed attempt

**Tech Profile**
- iPhone 13, campus Wi-Fi (inconsistent), Safari
- Situational: thumb-only input, glare on screen between classes, distracted attention
- 3 browser tabs max, mostly Instagram and iMessage
```

## Anti-Persona

Include one anti-persona — someone the product is explicitly NOT for. This
prevents wasted testing time and reveals where the product's boundaries are.

Format: `## Anti-Persona: Name — Reason`

```markdown
## Anti-Persona: Enterprise HR Director

> "I need SSO, audit logs, and a 200-seat license managed through our procurement system."

This is NOT the target user. The product is designed for individual students, not
enterprise buyers. Testing from this perspective would surface feature requests
that are intentionally out of scope, not bugs.

**Why they're excluded**: enterprise procurement needs, compliance requirements,
and admin-panel expectations are not part of the product's mission.
```

## Diversity Checklist

Across all personas, cover:
- [ ] At least one mobile-primary user
- [ ] At least one user with accessibility needs (screen reader, keyboard-only, low vision)
- [ ] At least one user with poor connectivity or old hardware
- [ ] At least one impatient/rushed user
- [ ] At least one methodical/thorough user
- [ ] At least one user unfamiliar with the product's domain
- [ ] Different levels of tech comfort
- [ ] Different emotional states (anxious, casual, skeptical, enthusiastic)
