from __future__ import annotations

import importlib.util
import subprocess
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
    assert 'style="--c:#b45309"' in html
    assert 'class="step-num">01</span>' in html
    assert 'class="meta">confusion</span>' in html
    assert 'class="narrative"' in html
    assert 'src="data:image/png;base64,abc123"' in html
    assert 'class="takeaway"' in html
    assert "Explain scoring where the user encounters it." in html


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


def test_template_uses_sans_headings_and_serif_takeaways():
    template = report.HTML_TEMPLATE

    assert "h1.display {{\n  font-family: var(--sans);" in template
    assert ".lede {{\n  font-family: var(--sans);" in template
    assert ".section-head h2 {{\n  font-family: var(--sans);" in template
    assert ".prose h1, .prose h2, .prose h4 {{" in template
    assert ".action-card .takeaway p {{" in template
    assert "font-family: var(--serif);" in template


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

    result = subprocess.run(
        ["uv", "run", str(MODULE_PATH), str(trial)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    html = (trial / "report.html").read_text(encoding="utf-8")
    assert "data:image/png;base64," in html
    assert 'class="journey-stream"' in html
    assert 'section id="comparison" class="bleed"' in html
    assert '<section id="reference">' in html
