# Trial Report Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign generated user-trial HTML reports so the journey reads as a legible first-person vertical story, comparison findings get enough width, and reference artifacts move below the findings.

**Architecture:** Keep `scripts/generate_trial_report.py` as the single report generator, but change its reaction model from scored chart points to narrative action cards. Add focused pytest coverage around reaction parsing, action-card rendering, section order, comparison bleed-out, collapsed reference artifacts, and optional table-of-contents links. Update both explorer agent prompts so new trial output writes first-person `Narrative` entries while the parser remains backward compatible with legacy `What happened` files; terminal trials can attach text-based "screenshots" through preserved `Terminal output` blocks.

**Tech Stack:** Python 3.10+, `uv run --script`, `markdown`, `bleach`, `pytest`, Markdown agent definitions, self-contained HTML/CSS.

---

## File Structure

- Create: `tests/test_generate_trial_report.py`
  - Unit and integration tests for reaction parsing and generated HTML.
  - Uses `importlib.util.spec_from_file_location` because `scripts/` is not a Python package.
- Modify: `scripts/generate_trial_report.py`
  - Replace valence-score journey chart with vertical action cards.
  - Parse `Narrative` with legacy fallback to `What happened`.
  - Parse `Terminal output` as preserved text evidence and render it inside action cards.
  - Render comparison as a wide bleed-out section.
  - Fold journal and discovered specs into collapsed reference details.
  - Keep screenshots embedded as base64 data URIs in cards and the plates strip.
- Modify: `agents/user-trial-explorer-browser.md`
  - Teach browser explorers to write first-person `Narrative` reactions and to copy saved screenshots into `<output-dir>/screenshots/`.
- Modify: `agents/user-trial-explorer-terminal.md`
  - Teach terminal explorers to write first-person `Narrative` reactions and text-based terminal "screenshots" as `Terminal output`.
- Reference only: `docs/superpowers/specs/2026-04-28-trial-report-redesign-design.md`
  - Source design document for this implementation.

## Resolved Design Decisions

- Optional sections must be omitted from the table of contents when they are not rendered. Reference is always rendered because journal/spec artifacts can show their own empty states.
- Terminal-mode "screenshots" are text-based. The terminal prompt should use `Terminal output`, the parser should preserve line breaks, and action cards should render that block as terminal evidence rather than overloading the image `Screenshot` field.
- The chip row is enough for the top-level emotional distribution. Do not add a sparkline, mini chart, or hover-sync summary in this redesign.

### Task 1: Test Reaction Parsing Contract

**Files:**
- Create: `tests/test_generate_trial_report.py`
- Modify: `scripts/generate_trial_report.py`

- [ ] **Step 1: Create the test module with an import helper**

Create `tests/test_generate_trial_report.py`:

```python
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_trial_report.py"


spec = importlib.util.spec_from_file_location("generate_trial_report", MODULE_PATH)
assert spec is not None
report = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = report
spec.loader.exec_module(report)
```

- [ ] **Step 2: Add a failing test for multi-line `Narrative` parsing**

Append:

```python
def test_parse_reactions_reads_multiline_narrative_and_screenshot_basename():
    reactions = report.parse_reactions(
        """
## Match scores have no scale

- **Reaction**: confusion
- **Narrative**: I see an 82% match, but I don't know what it means.
  I try looking for a scale or explanation and there just isn't one.
  Now I'm wondering if this is personalized or just made up.
- **Why it matters**: Scores need nearby explanation before users trust them.
- **Screenshot**: screenshots/01-score.png
"""
    )

    assert len(reactions) == 1
    assert reactions[0].title == "Match scores have no scale"
    assert reactions[0].reaction == "confusion"
    assert reactions[0].narrative == (
        "I see an 82% match, but I don't know what it means. "
        "I try looking for a scale or explanation and there just isn't one. "
        "Now I'm wondering if this is personalized or just made up."
    )
    assert reactions[0].why_matters == (
        "Scores need nearby explanation before users trust them."
    )
    assert reactions[0].screenshot == "01-score.png"
```

- [ ] **Step 3: Add a failing test for legacy `What happened` fallback**

Append:

```python
def test_parse_reactions_falls_back_to_legacy_what_happened():
    reactions = report.parse_reactions(
        """
## Empty search

- **Reaction**: anxiety
- **What happened**: Search returned nothing and gave no recovery path.
- **Why it matters**: Empty states need next steps.
- **Screenshot**: N/A
"""
    )

    assert reactions[0].reaction == "anxiety"
    assert reactions[0].narrative == "Search returned nothing and gave no recovery path."
    assert reactions[0].screenshot is None
```

- [ ] **Step 4: Add a failing test for terminal text screenshots**

Append:

```python
def test_parse_reactions_preserves_terminal_output_as_text_screenshot():
    reactions = report.parse_reactions(
        """
## Missing help output

- **Reaction**: frustration
- **Narrative**: I run the help command and it dumps a wall of flags.
- **Why it matters**: CLI help needs a readable first screen.
- **Terminal output**: $ blindspots --help
  Usage: blindspots [command]
  Error: unknown option --persona
"""
    )

    assert reactions[0].terminal_output == (
        "$ blindspots --help\n"
        "Usage: blindspots [command]\n"
        "Error: unknown option --persona"
    )
```

- [ ] **Step 5: Run parser tests and verify they fail on the old implementation**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py -q
```

Expected before implementation: FAIL because `Reaction` has no `narrative` or `terminal_output` field and multi-line fields are not captured correctly.

- [ ] **Step 6: Replace scored reaction vocabulary with category lanes**

In `scripts/generate_trial_report.py`, replace `REACTION_SCORES` with:

```python
REACTION_LANES = [
    "delight",
    "surprise",
    "indifference",
    "confusion",
    "anxiety",
    "frustration",
]
```

Keep `REACTION_COLORS` with these exact category colors:

```python
REACTION_COLORS = {
    "delight": "#15803d",
    "surprise": "#0e7490",
    "indifference": "#525252",
    "confusion": "#b45309",
    "anxiety": "#6d28d9",
    "frustration": "#b91c1c",
}
```

- [ ] **Step 7: Rename the reaction payload fields**

Change:

```python
@dataclass
class Reaction:
    title: str
    reaction: str
    what_happened: str
    why_matters: str = ""
    screenshot: str | None = None
```

To:

```python
@dataclass
class Reaction:
    title: str
    reaction: str
    narrative: str
    why_matters: str = ""
    screenshot: str | None = None
    terminal_output: str = ""
```

- [ ] **Step 8: Implement multi-line field parsing, legacy fallback, and preserved terminal output**

Inside `parse_reactions`, replace the `grab()` implementation with:

```python
def grab(field_name: str, *, collapse: bool = True) -> str:
    m = re.search(
        rf"""^\s*[-*]\s*\*\*{re.escape(field_name)}\*\*\s*:\s*
             (?P<val>.+?)
             (?=^\s*[-*]\s*\*\*[^*]+\*\*\s*:|\Z)""",
        body,
        re.MULTILINE | re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )
    if not m:
        return ""
    val = m.group("val").strip()
    if collapse:
        return re.sub(r"\s+", " ", val).strip()
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in val.splitlines()
    ).strip()
```

Use `REACTION_LANES` when recognizing category words, and construct reactions with:

```python
Reaction(
    title=title,
    reaction=reaction_word,
    narrative=grab("Narrative") or grab("What happened"),
    why_matters=grab("Why it matters"),
    screenshot=screenshot,
    terminal_output=grab("Terminal output", collapse=False),
)
```

- [ ] **Step 9: Run parser tests and verify they pass**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py::test_parse_reactions_reads_multiline_narrative_and_screenshot_basename tests/test_generate_trial_report.py::test_parse_reactions_falls_back_to_legacy_what_happened tests/test_generate_trial_report.py::test_parse_reactions_preserves_terminal_output_as_text_screenshot -q
```

Expected: PASS.

- [ ] **Step 10: Commit parser contract**

```bash
git add tests/test_generate_trial_report.py scripts/generate_trial_report.py
git commit -m "Support narrative reactions in trial reports"
```

### Task 2: Render Vertical Journey Action Cards

**Files:**
- Modify: `tests/test_generate_trial_report.py`
- Modify: `scripts/generate_trial_report.py`

- [ ] **Step 1: Add a failing test for action-card HTML**

Append:

```python
def test_render_journey_spread_outputs_action_cards_with_takeaways():
    reactions = [
        report.Reaction(
            title="Match scores have no scale",
            reaction="confusion",
            narrative="I see the score, but I can't tell if 82% is good.",
            why_matters="Explain scoring where the user encounters it.",
            screenshot="01-score.png",
        )
    ]
    screenshots = {"01-score.png": "data:image/png;base64,abc123"}

    html = report.render_journey_spread(reactions, screenshots)

    assert 'class="journey-stream"' in html
    assert 'class="action-card"' in html
    assert "style=\"--c:#b45309\"" in html
    assert 'class="step-num">01</span>' in html
    assert 'class="meta">confusion</span>' in html
    assert 'class="narrative"' in html
    assert 'src="data:image/png;base64,abc123"' in html
    assert 'class="takeaway"' in html
    assert "Explain scoring where the user encounters it." in html
```

- [ ] **Step 2: Add a failing test for terminal text evidence inside action cards**

Append:

```python
def test_render_journey_spread_outputs_terminal_text_screenshot():
    reactions = [
        report.Reaction(
            title="Help output is hard to scan",
            reaction="frustration",
            narrative="I run help and immediately lose the path.",
            why_matters="CLI help needs a readable first screen.",
            terminal_output="$ blindspots --help\nUsage: blindspots [command]",
        )
    ]

    html = report.render_journey_spread(reactions, {})

    assert 'class="terminal-output"' in html
    assert "$ blindspots --help" in html
    assert "Usage: blindspots [command]" in html
```

- [ ] **Step 3: Run the new journey rendering tests and verify they fail**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py::test_render_journey_spread_outputs_action_cards_with_takeaways tests/test_generate_trial_report.py::test_render_journey_spread_outputs_terminal_text_screenshot -q
```

Expected before implementation: FAIL because `render_journey_spread` does not exist.

- [ ] **Step 4: Replace chart rendering functions**

Remove `render_emotion_journey`. Add:

```python
def render_action_card(i: int, r: Reaction, screenshots: dict[str, str]) -> str:
    color = REACTION_COLORS.get(r.reaction, REACTION_COLORS["indifference"])
    heading = r.title or r.reaction.title()

    img_html = ""
    if r.screenshot and r.screenshot in screenshots:
        img_html = (
            f'<img src="{screenshots[r.screenshot]}" '
            f'alt="{html.escape(r.screenshot)}" loading="lazy">'
        )

    narrative_html = (
        f'<p class="narrative">{html.escape(r.narrative)}</p>' if r.narrative else ""
    )
    terminal_html = (
        f'<pre class="terminal-output"><code>{html.escape(r.terminal_output)}</code></pre>'
        if r.terminal_output else ""
    )
    takeaway_html = (
        f'<aside class="takeaway"><span class="takeaway-label">Takeaway</span>'
        f'<p>{html.escape(r.why_matters)}</p></aside>'
        if r.why_matters else ""
    )

    return (
        f'<article class="action-card" style="--c:{color}">'
        f'<header class="action-head">'
        f'<span class="step-num">{i:02d}</span>'
        f'<span class="meta">{html.escape(r.reaction)}</span>'
        f'</header>'
        f'<h3 class="heading">{html.escape(heading)}</h3>'
        f'{narrative_html}'
        f'{img_html}'
        f'{terminal_html}'
        f'{takeaway_html}'
        f'</article>'
    )
```

Then add:

```python
def render_journey_spread(
    reactions: list[Reaction], screenshots: dict[str, str]
) -> str:
    if not reactions:
        return ""
    cards = "".join(
        render_action_card(i, r, screenshots)
        for i, r in enumerate(reactions, start=1)
    )
    return f'<div class="journey-stream">{cards}</div>'
```

- [ ] **Step 5: Replace journey chart CSS with action-card CSS**

In `HTML_TEMPLATE`, remove the `figure.journey`, `.journey-head`, `.journey-grid`, `.axis`, `.track`, and `.numbers` CSS rules. Add CSS for:

```css
.journey-stream {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.action-card {
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-left: 3px solid var(--c, var(--rule));
  border-radius: 0 5px 5px 0;
  padding: 16px 22px 18px;
  box-shadow: var(--shadow);
}
.action-card .action-head {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 10px;
}
.action-card .step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border: 2px solid var(--c, var(--rule));
  border-radius: 50%;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--c, var(--ink-2));
  background: var(--surface);
  flex-shrink: 0;
}
.action-card .meta {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--c, var(--muted));
}
.action-card .heading {
  font-family: var(--sans);
  font-size: 18px;
  font-weight: 600;
  line-height: 1.35;
  color: var(--ink);
  margin: 0 0 12px;
}
.action-card .narrative {
  font-size: 15px;
  line-height: 1.6;
  color: var(--ink-2);
  margin: 0 0 12px;
}
.action-card img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 14px 0 0;
  border-radius: 4px;
  border: 1px solid var(--hairline);
}
.action-card .terminal-output {
  margin: 14px 0 0;
  padding: 12px 14px;
  border-radius: 4px;
  border: 1px solid var(--hairline);
  background: #1a1a1a;
  color: #f4f0e6;
  overflow-x: auto;
  font-family: var(--mono);
  font-size: 12px;
  line-height: 1.55;
}
.action-card .terminal-output code {
  font-family: inherit;
}
.action-card .takeaway {
  margin-top: 14px;
  padding: 10px 14px;
  background: color-mix(in oklab, var(--c, var(--rule)) 6%, transparent);
  border-radius: 3px;
}
.action-card .takeaway-label {
  display: inline-block;
  font-family: var(--mono);
  font-size: 9.5px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--c, var(--muted));
  margin-bottom: 3px;
}
.action-card .takeaway p {
  font-family: var(--serif);
  font-style: italic;
  font-size: 14px;
  line-height: 1.5;
  color: var(--ink);
  margin: 0;
  font-variation-settings: "opsz" 24;
}
```

- [ ] **Step 6: Wire the journey section to the new renderer**

In `render_html`, replace calls to `render_emotion_journey` with:

```python
journey_spread = render_journey_spread(data.reactions, data.screenshots)
```

Render the section as:

```python
journey_section = (
    '<section id="journey">'
    '<header class="section-head">'
    '<div class="numeral">§I</div>'
    '<div>'
    '<div class="label">The trial</div>'
    '<h2>Journey</h2>'
    '</div>'
    '</header>'
    f'{journey_spread}'
    '</section>'
)
```

- [ ] **Step 7: Run journey rendering tests**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit vertical journey**

```bash
git add tests/test_generate_trial_report.py scripts/generate_trial_report.py
git commit -m "Render trial journey as action cards"
```

### Task 3: Reorder Sections And Widen Comparison

**Files:**
- Modify: `tests/test_generate_trial_report.py`
- Modify: `scripts/generate_trial_report.py`

- [ ] **Step 1: Add a failing integration test for section order and classes**

Append:

```python
def test_render_html_orders_sections_and_bleeds_comparison():
    data = report.TrialData(
        persona_name="Priya",
        persona_slug="priya",
        journal_md="# Journal\n\nTried search.",
        specs_md="## Search\n\n**DISC-1** Search exists.",
        comparison_md="| Actual | Discovered | Gap |\n|---|---|---|\n| A | B | C |",
        reactions=[
            report.Reaction(
                title="Search felt vague",
                reaction="confusion",
                narrative="I typed economics and got finance.",
                why_matters="Search labels need to match user language.",
            )
        ],
    )

    html = report.render_html(data)

    assert html.index('id="journey"') < html.index('id="comparison"')
    assert html.index('id="comparison"') < html.index('id="reference"')
    assert 'section id="comparison" class="bleed"' in html
    assert 'class="card prose prose-wide"' in html
    assert '<div class="numeral">§I</div>' in html
    assert '<div class="numeral">§II</div>' in html
    assert '<div class="numeral">§III</div>' in html
    assert '<summary>Exploration journal</summary>' in html
    assert '<summary>Discovered specs</summary>' in html
    assert 'id="reactions"' not in html
```

- [ ] **Step 2: Add a failing test for optional TOC links**

Append:

```python
def test_toc_only_links_to_rendered_optional_sections():
    data = report.TrialData(
        persona_name="Sparse",
        persona_slug="sparse",
        journal_md="Only notes.",
        specs_md="Only specs.",
        reactions=[],
        comparison_md="",
        screenshots={},
    )

    html = report.render_html(data)

    assert '<a href="#reference">Reference</a>' in html
    assert '<a href="#comparison">Comparison</a>' not in html
    assert '<a href="#screenshots">Screenshots</a>' not in html
    assert '<a href="#journey">Journey</a>' not in html
```

- [ ] **Step 3: Run the section tests and verify they fail**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py::test_render_html_orders_sections_and_bleeds_comparison tests/test_generate_trial_report.py::test_toc_only_links_to_rendered_optional_sections -q
```

Expected before implementation: FAIL because section order/classes and dynamic TOC behavior are not yet implemented.

- [ ] **Step 4: Add wide comparison CSS**

In `HTML_TEMPLATE`, after `.card`, add:

```css
section.bleed {
  width: min(1240px, calc(100vw - 32px));
  margin-left: 50%;
  transform: translateX(-50%);
}
.prose.prose-wide { max-width: none; }
.prose.prose-wide table { font-size: 13px; }
.prose.prose-wide td, .prose.prose-wide th { padding: 8px 10px; }
```

- [ ] **Step 5: Change the body template section order**

In `HTML_TEMPLATE`, remove standalone `#reactions`, standalone `#discovered-specs`, and standalone `#journal` sections. Keep placeholders in this order:

```html
{journey_section}

{comparison_section}

<section id="reference">
  ...
</section>

{screenshots_section}
```

The reference section should contain two collapsed details:

```html
<details class="journal" id="journal">
  <summary>Exploration journal</summary>
  <div class="body prose">{journal_html}</div>
</details>
<details class="journal" id="discovered-specs">
  <summary>Discovered specs</summary>
  <div class="body prose">{specs_html}</div>
</details>
```

- [ ] **Step 6: Render comparison as Section II**

In `render_html`, render `comparison_section` only when `data.comparison_md.strip()` is truthy:

```python
comparison_section = (
    '<section id="comparison" class="bleed">'
    '<header class="section-head">'
    '<div class="numeral">§II</div>'
    '<div>'
    '<div class="label">Findings</div>'
    '<h2>Comparison vs actual specs</h2>'
    '</div>'
    '</header>'
    f'<div class="card prose prose-wide">{md_to_html(data.comparison_md, data.screenshots)}</div>'
    "</section>"
)
```

- [ ] **Step 7: Build the TOC from rendered sections**

Replace the static `toc` list with section-aware construction:

```python
toc: list[tuple[str, str]] = []
if data.reactions:
    toc.append(("#journey", "Journey"))
if data.comparison_md.strip():
    toc.append(("#comparison", "Comparison"))
toc.append(("#reference", "Reference"))
if data.screenshots:
    toc.append(("#screenshots", "Screenshots"))
```

- [ ] **Step 8: Run full report tests**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit section reordering**

```bash
git add tests/test_generate_trial_report.py scripts/generate_trial_report.py
git commit -m "Reorder trial report sections around comparison"
```

### Task 4: Update Typography

**Files:**
- Modify: `tests/test_generate_trial_report.py`
- Modify: `scripts/generate_trial_report.py`

- [ ] **Step 1: Add a failing CSS contract test**

Append:

```python
def test_template_uses_sans_headings_and_serif_takeaways():
    template = report.HTML_TEMPLATE

    assert "h1.display {{\n  font-family: var(--sans);" in template
    assert ".lede {{\n  font-family: var(--sans);" in template
    assert ".section-head h2 {{\n  font-family: var(--sans);" in template
    assert ".prose h1, .prose h2, .prose h4 {{" in template
    assert ".action-card .takeaway p {{" in template
    assert "font-family: var(--serif);" in template
```

- [ ] **Step 2: Run the CSS contract test and verify it fails**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py::test_template_uses_sans_headings_and_serif_takeaways -q
```

Expected before implementation: FAIL because large headings still use the serif display style.

- [ ] **Step 3: Switch large headings and lede to Manrope**

In `HTML_TEMPLATE`, update:

- `h1.display` to `font-family: var(--sans); font-weight: 700; font-size: clamp(44px, 7.5vw, 84px); line-height: 1.02;`
- `.lede` to `font-family: var(--sans); font-weight: 400; font-size: 20px; line-height: 1.45;`
- `.section-head h2` to `font-family: var(--sans); font-weight: 700; font-size: 28px; line-height: 1.15;`
- `.prose h1, .prose h2, .prose h4` to `font-family: var(--sans); font-weight: 700;`

Keep `.section-head .numeral` and `.action-card .takeaway p` on `var(--serif)`.

- [ ] **Step 4: Run CSS contract and full tests**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit typography changes**

```bash
git add tests/test_generate_trial_report.py scripts/generate_trial_report.py
git commit -m "Use sans headings in trial report"
```

### Task 5: Update Explorer Agent Reaction Prompts

**Files:**
- Modify: `agents/user-trial-explorer-browser.md`
- Modify: `agents/user-trial-explorer-terminal.md`

- [ ] **Step 1: Update browser screenshot instructions**

In `agents/user-trial-explorer-browser.md`, expand allowed Bash usage to include copying saved screenshots into `<output-dir>/screenshots/`.

Add a `Capturing screenshots` block that instructs browser agents to:

- use browser/computer screenshot capture with `save_to_disk: true`
- copy the returned file path into `<output-dir>/screenshots/<NN>-<short-slug>.png`
- use sortable two-digit prefixes
- reference the exact filename in `reactions.md` and `discovered-specs.md`
- use an image extension supported by the report generator

- [ ] **Step 2: Update browser reaction template**

Replace the browser `REACT` template fields:

```markdown
- **What happened**: <one sentence>
- **Why it matters**: <what this tells us about the UX>
- **Screenshot**: <filename if captured>
```

With:

```markdown
- **Narrative**: <3-6 sentences in first-person voice. What you saw, what
  went through your head, what you tried, how you felt. Use contractions,
  ellipses, asides - sound human.>
- **Why it matters**: <one-sentence takeaway about what this reveals - the
  UX issue, the assumption being made, the gap. Keep it short and
  analytical; the narrative above already carries the emotion.>
- **Screenshot**: <filename.png if captured, e.g. `01-search-empty.png`>
```

Add this rule immediately after the template:

```markdown
Don't analyze inside the narrative - narrate. The "Why it matters" line
is where you step back and label the issue.
```

- [ ] **Step 3: Update browser discovered-spec screenshot example**

Change:

```markdown
- Screenshot: <filename if captured>
```

To:

```markdown
- Screenshot: <filename.png if captured, e.g. `01-search-empty.png`>
```

- [ ] **Step 4: Update terminal reaction template and text screenshot guidance**

In `agents/user-trial-explorer-terminal.md`, replace the terminal `REACT` template fields:

```markdown
- **What happened**: <one sentence>
- **Why it matters**: <what this tells us about the UX>
- **Terminal output**: <relevant command + output snippet if useful>
```

With:

```markdown
- **Narrative**: <3-6 sentences in first-person voice. What you ran, what
  came back, what went through your head, what you tried next, how you
  felt. Use contractions, ellipses, asides - sound human.>
- **Why it matters**: <one-sentence takeaway about what this reveals.
  Keep it short and analytical; the narrative carries the emotion.>
- **Terminal output**: <text-based screenshot: the exact command plus the
  important output lines, preserving line breaks. Keep it short enough to
  scan in the report.>
```

Add this rule immediately after the template:

```markdown
Don't analyze inside the narrative - narrate. The "Why it matters" line
is where you step back and label the issue.
```

- [ ] **Step 5: Verify old field name is gone and terminal evidence remains**

Run:

```bash
rg -n "What happened|\\*\\*Narrative\\*\\*|\\*\\*Terminal output\\*\\*" agents/user-trial-explorer-browser.md agents/user-trial-explorer-terminal.md
```

Expected: `**Narrative**` matches in both files, `**Terminal output**` matches in terminal mode, and no `What happened` matches.

- [ ] **Step 6: Commit prompt updates**

```bash
git add agents/user-trial-explorer-browser.md agents/user-trial-explorer-terminal.md
git commit -m "Prompt trial explorers for narrative reactions"
```

### Task 6: End-To-End Report Generation And Visual Smoke Check

**Files:**
- Modify: `tests/test_generate_trial_report.py`
- Modify: `scripts/generate_trial_report.py` if defects are found

- [ ] **Step 1: Add a CLI smoke test using a temporary trial directory**

Append:

```python
def test_cli_generates_self_contained_report(tmp_path):
    trial = tmp_path / "maya"
    shots = trial / "screenshots"
    shots.mkdir(parents=True)
    (trial / "journal.md").write_text("# Journal - Maya\n\nTried onboarding.", encoding="utf-8")
    (trial / "discovered-specs.md").write_text("## Onboarding\n\n- Screenshot: 01-home.png", encoding="utf-8")
    (trial / "comparison.md").write_text("| Actual | Discovered | Gap |\n|---|---|---|\n| A | B | C |", encoding="utf-8")
    (trial / "reactions.md").write_text(
        """## Home page

- **Reaction**: surprise
- **Narrative**: I expected a dashboard, but I got a guided start.
- **Why it matters**: First screens set expectations.
- **Screenshot**: 01-home.png
""",
        encoding="utf-8",
    )
    (shots / "01-home.png").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02"
        b"\x00\x00\x00\x90wS\xde"
    )

    assert report.main_for_test([str(trial)]) == 0
    html = (trial / "report.html").read_text(encoding="utf-8")

    assert "data:image/png;base64," in html
    assert 'class="journey-stream"' in html
    assert 'section id="comparison" class="bleed"' in html
    assert '<section id="reference">' in html
```

This test requires a tiny `main_for_test(argv: list[str]) -> int` wrapper. If adding that wrapper feels too invasive, replace the test with `subprocess.run(["uv", "run", str(MODULE_PATH), str(trial)], ...)`.

- [ ] **Step 2: Add testable CLI wrapper or subprocess smoke path**

Preferred small wrapper in `scripts/generate_trial_report.py`:

```python
def main_for_test(argv: list[str]) -> int:
    return main(argv)
```

Then change `main()` to accept an optional `argv`:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    ...
    args = parser.parse_args(argv)
```

- [ ] **Step 3: Run full tests**

Run:

```bash
uv run --with pytest --with markdown --with bleach pytest tests/test_generate_trial_report.py -q
```

Expected: PASS.

- [ ] **Step 4: Generate a manual sample report**

Run:

```bash
tmpdir="$(mktemp -d)"
mkdir -p "$tmpdir/maya/screenshots"
cat > "$tmpdir/maya/journal.md" <<'EOF'
# Journal - Maya

Tried onboarding and search.
EOF
cat > "$tmpdir/maya/discovered-specs.md" <<'EOF'
## Search

**DISC-1** When a user searches, the system should show matching roles.
- Evidence: Search returned finance-heavy results.
- Confidence: medium
- Reaction: confusion
EOF
cat > "$tmpdir/maya/comparison.md" <<'EOF'
| Actual | Discovered | Gap |
|---|---|---|
| Search ranks by employer criteria | User expected field-of-study match | Ranking explanation is undiscoverable |
EOF
cat > "$tmpdir/maya/reactions.md" <<'EOF'
## Match scores have no scale

- **Reaction**: confusion
- **Narrative**: I see an 82% match, but I don't know what it means. I try looking for a scale or explanation and there just isn't one. Now I'm wondering if this is personalized or just made up.
- **Why it matters**: Scores need nearby explanation before users trust them.
- **Screenshot**: N/A
EOF
uv run scripts/generate_trial_report.py "$tmpdir/maya"
```

Expected: command prints `Wrote ...report.html` with `1 reactions`.

- [ ] **Step 5: Inspect the generated HTML manually**

Open the generated `report.html` in a browser and verify:

- Journey is Section I and renders as stacked action cards.
- Terminal-mode `Terminal output` renders as a preserved text evidence block when present.
- No valence labels (`alarm`, `tension`, `neutral`, `positive`) appear.
- Comparison is Section II and wider than the main prose column.
- Reference is Section III with collapsed journal and discovered specs.
- Screenshots section is omitted when no screenshots exist.
- TOC does not link to omitted optional sections.
- Heading text uses Manrope/sans styling; only section numerals and takeaway text retain Fraunces.

- [ ] **Step 6: Commit verification support**

```bash
git add tests/test_generate_trial_report.py scripts/generate_trial_report.py
git commit -m "Add trial report generation tests"
```

### Task 7: Final Verification

**Files:**
- Read: `scripts/generate_trial_report.py`
- Read: `agents/user-trial-explorer-browser.md`
- Read: `agents/user-trial-explorer-terminal.md`
- Read: `tests/test_generate_trial_report.py`

- [ ] **Step 1: Run all automated checks**

```bash
uv run --with pytest --with markdown --with bleach pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Check for removed valence vocabulary in generator**

```bash
rg -n "REACTION_SCORES|alarm|tension|positive|neutral|render_emotion_journey|what_happened" scripts/generate_trial_report.py
```

Expected: no matches.

- [ ] **Step 3: Check prompt schema**

```bash
rg -n "What happened|\\*\\*Narrative\\*\\*|\\*\\*Terminal output\\*\\*" agents/user-trial-explorer-browser.md agents/user-trial-explorer-terminal.md
```

Expected: `**Narrative**` matches in both files, `**Terminal output**` matches in terminal mode, and no `What happened` matches.

- [ ] **Step 4: Review generated diff**

```bash
git diff --stat HEAD
git diff -- scripts/generate_trial_report.py
git diff -- agents/user-trial-explorer-browser.md agents/user-trial-explorer-terminal.md
git diff -- tests/test_generate_trial_report.py
```

Expected: only planned files changed.

- [ ] **Step 5: Commit any remaining uncommitted changes**

```bash
git add scripts/generate_trial_report.py agents/user-trial-explorer-browser.md agents/user-trial-explorer-terminal.md tests/test_generate_trial_report.py
git commit -m "Redesign trial HTML report"
```

## Review Notes

- The design doc says the branch already contains an implementation. If executing this plan in the current branch, start by comparing the dirty diff to each task and only add missing tests or refinements; do not overwrite user changes blindly.
- The design decisions are now resolved: omit optional missing sections from the TOC, render terminal-mode evidence as text-based `Terminal output`, and keep the chip row as the only emotional distribution summary.
- The `main_for_test` wrapper in Task 6 is optional. If keeping the script's current CLI shape is preferred, use a subprocess test instead and avoid changing the CLI function signature.
