#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown>=3.5", "bleach>=6.1"]
# ///
"""Generate a self-contained HTML report from a user-trial output directory.

Usage:
    uv run scripts/generate_trial_report.py <trial-dir>

Reads journal.md, discovered-specs.md, reactions.md, comparison.md plus any
PNG/JPG files under screenshots/, and emits report.html in the same directory.
Screenshots are embedded as base64 data URIs so the file is shareable as a
single attachment.
"""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import bleach
import markdown


# Sanitization allowlist for markdown-rendered HTML.
# Trial source files (journal.md, reactions.md, etc.) are written by an agent
# exploring third-party apps — the content can include arbitrary text quoted
# from those pages. Any raw HTML (script tags, onerror handlers, javascript:
# URIs) reaching the rendered report would execute when someone opens it.
ALLOWED_TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "strong", "em", "b", "i",
    "code", "pre",
    "blockquote",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr", "br",
    "span", "div",
}
ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "loading"],
}
# `data:` is required for inline base64 screenshots; without it bleach strips
# every embedded image. Browsers don't execute JS in `data:image/*` URIs.
ALLOWED_PROTOCOLS = ["http", "https", "data", "mailto"]


def sanitize_rendered_html(rendered: str) -> str:
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )


REACTION_LANES = [
    "delight",
    "surprise",
    "indifference",
    "confusion",
    "anxiety",
    "frustration",
]

REACTION_COLORS = {
    "delight": "#15803d",
    "surprise": "#0e7490",
    "indifference": "#525252",
    "confusion": "#b45309",
    "anxiety": "#6d28d9",
    "frustration": "#b91c1c",
}


@dataclass
class Reaction:
    title: str
    reaction: str
    narrative: str  # first-person paragraph; legacy data may have used "What happened"
    why_matters: str = ""
    screenshot: str | None = None
    terminal_output: str = ""


@dataclass
class TrialData:
    persona_name: str
    persona_slug: str
    journal_md: str = ""
    specs_md: str = ""
    reactions_md: str = ""
    comparison_md: str = ""
    reactions: list[Reaction] = field(default_factory=list)
    screenshots: dict[str, str] = field(default_factory=dict)


def read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def encode_image(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def parse_reactions(text: str) -> list[Reaction]:
    """Parse `## Title` blocks into Reaction records.

    Tolerant: missing fields just become empty strings. Stops at the next
    `## ` heading or end of file.
    """
    blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)
    reactions: list[Reaction] = []
    for block in blocks[1:]:  # first chunk is anything before the first heading
        lines = block.splitlines()
        title = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:])

        def grab(field_name: str, *, collapse: bool = True) -> str:
            # Field value runs from the marker line through any indented
            # continuation lines, stopping at the next `- **Field**:` or EOF.
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
                # Collapse the multi-line indented continuation into one paragraph.
                return re.sub(r"\s+", " ", val).strip()
            return "\n".join(
                line[2:] if line.startswith("  ") else line
                for line in val.splitlines()
            ).strip()

        reaction_word = grab("Reaction").lower()
        # Take the first recognized word if the line is a list of options.
        for word in REACTION_LANES:
            if word in reaction_word:
                reaction_word = word
                break
        else:
            reaction_word = "indifference"

        screenshot_raw = grab("Screenshot")
        screenshot = None
        if screenshot_raw and screenshot_raw.lower() not in {"n/a", "none", ""}:
            screenshot = Path(screenshot_raw).name

        reactions.append(
            Reaction(
                title=title,
                reaction=reaction_word,
                narrative=grab("Narrative") or grab("What happened"),
                why_matters=grab("Why it matters"),
                screenshot=screenshot,
                terminal_output=grab("Terminal output", collapse=False),
            )
        )
    return reactions


def truncate_label(text: str, max_len: int = 80) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def render_action_card(i: int, r: Reaction, screenshots: dict[str, str]) -> str:
    """One step in the journey — heading, persona's first-person narrative,
    optional takeaway summary, optional screenshot."""
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


def render_journey_spread(
    reactions: list[Reaction], screenshots: dict[str, str]
) -> str:
    """Single-column journey: each step is a card showing the persona's
    reaction (heading, what happened, why it matters, optional screenshot).
    Emotion is conveyed by the card's left-border color, step number ring,
    and meta label — no separate chart needed."""
    if not reactions:
        return ""

    cards = "".join(
        render_action_card(i, r, screenshots)
        for i, r in enumerate(reactions, start=1)
    )

    return f'<div class="journey-stream">{cards}</div>'


_IMG_TAG = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)
_SRC_ATTR = re.compile(r'\bsrc=(?P<q>["\'])(?P<val>[^"\']+)(?P=q)', re.IGNORECASE)


def rewrite_image_refs(html_body: str, screenshots: dict[str, str]) -> str:
    """Rewrite <img src="foo.png"> to data URIs when basename matches a known screenshot."""

    def repl(match: re.Match[str]) -> str:
        attrs = match.group(1)
        src_m = _SRC_ATTR.search(attrs)
        if not src_m:
            return match.group(0)
        name = Path(src_m.group("val")).name
        if name not in screenshots:
            return match.group(0)
        new_attrs = _SRC_ATTR.sub(f'src="{screenshots[name]}"', attrs)
        if "loading=" not in new_attrs.lower():
            new_attrs += ' loading="lazy"'
        return f"<img{new_attrs}>"

    return _IMG_TAG.sub(repl, html_body)


SCREENSHOT_LINE = re.compile(
    r"""(?im)^(?P<prefix>\s*[-*]\s*(?:\*\*)?Screenshot(?:\*\*)?\s*:\s*)
        (?P<name>[\w./-]+\.(?:png|jpe?g|gif|webp))\s*$""",
    re.VERBOSE,
)


def inline_screenshot_refs(text: str, screenshots: dict[str, str]) -> str:
    """Promote `- Screenshot: foo.png` lines to inline images we can embed.

    Authors write the filename as plain text in discovered-specs.md and
    reactions.md. Without this step those references stay as text and the
    images only appear in the bottom strip.
    """

    def repl(m: re.Match[str]) -> str:
        name = Path(m.group("name")).name
        if name not in screenshots:
            return m.group(0)
        return f'{m.group("prefix")}[{name}]({name})\n\n![{name}]({name})'

    return SCREENSHOT_LINE.sub(repl, text)


def md_to_html(text: str, screenshots: dict[str, str]) -> str:
    if not text.strip():
        return '<p class="empty">No content.</p>'
    text = inline_screenshot_refs(text, screenshots)
    body = markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html",
    )
    body = rewrite_image_refs(body, screenshots)
    # Strip any raw HTML / event handlers / dangerous URI schemes that
    # markdown preserved. Trial files are written from untrusted page content.
    return sanitize_rendered_html(body)


def collect_data(trial_dir: Path) -> TrialData:
    persona_slug = trial_dir.name
    persona_name = persona_slug.replace("-", " ").title()
    data = TrialData(persona_name=persona_name, persona_slug=persona_slug)

    data.journal_md = read_optional(trial_dir / "journal.md")
    data.specs_md = read_optional(trial_dir / "discovered-specs.md")
    data.reactions_md = read_optional(trial_dir / "reactions.md")
    data.comparison_md = read_optional(trial_dir / "comparison.md")

    shots_dir = trial_dir / "screenshots"
    if shots_dir.is_dir():
        for path in sorted(shots_dir.iterdir()):
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                data.screenshots[path.name] = encode_image(path)

    data.reactions = parse_reactions(data.reactions_md)

    # Try to recover a nicer persona name from the journal's first H1.
    m = re.search(r"^#\s+(.+)$", data.journal_md, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        # Strip common prefixes like "Journal — Priya" or "Trial Journal: Priya"
        title = re.sub(r"^(?:trial\s+)?journal\s*[—:-]\s*", "", title, flags=re.IGNORECASE)
        if title:
            data.persona_name = title

    return data


def render_reaction_chips(reactions: list[Reaction]) -> str:
    if not reactions:
        return ""
    counts: dict[str, int] = {}
    for r in reactions:
        counts[r.reaction] = counts.get(r.reaction, 0) + 1
    chips = []
    for word, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        color = REACTION_COLORS.get(word, "#737373")
        chips.append(
            f'<span class="chip" style="background:{color}1a;color:{color};border-color:{color}66">'
            f'{html.escape(word)} · {n}</span>'
        )
    return '<div class="chips">' + "".join(chips) + "</div>"


def render_screenshot_strip(screenshots: dict[str, str]) -> str:
    if not screenshots:
        return ""
    items = []
    for name, src in screenshots.items():
        items.append(
            f'<figure><img src="{src}" alt="{html.escape(name)}" loading="lazy">'
            f'<figcaption>{html.escape(name)}</figcaption></figure>'
        )
    return '<div class="strip">' + "".join(items) + "</div>"


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..900&family=Manrope:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --paper: #fbfaf7;
  --paper-2: #f4f0e6;
  --surface: #ffffff;
  --ink: #171717;
  --ink-2: #2c2c2c;
  --muted: #6b6357;
  --hairline: #e8e2d2;
  --rule: #cfc6b0;
  --accent: #b8412e;
  --accent-soft: #f3dcd4;
  --shadow: 0 1px 0 rgba(23,23,23,.04), 0 4px 16px -8px rgba(23,23,23,.08);
  --serif: "Fraunces", "Iowan Old Style", "Georgia", serif;
  --sans: "Manrope", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --measure: 68ch;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
html {{ background: var(--paper); }}
body {{
  font-family: var(--sans);
  background:
    radial-gradient(1200px 600px at 20% -10%, #fdf6e8 0%, transparent 60%),
    radial-gradient(1000px 500px at 100% 0%, #f7e7df 0%, transparent 55%),
    var(--paper);
  color: var(--ink);
  font-size: 16px;
  line-height: 1.6;
  font-feature-settings: "ss01", "ss02", "cv11";
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
::selection {{ background: var(--accent-soft); color: var(--ink); }}
.report {{ max-width: 980px; margin: 0 auto; padding: 56px 32px 96px; }}

.hero {{ position: relative; padding: 32px 0 56px; border-bottom: 1px solid var(--hairline); margin-bottom: 64px; }}
.masthead {{
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); padding-bottom: 24px; border-bottom: 1px solid var(--hairline); margin-bottom: 40px;
}}
.masthead .brand {{ display: flex; align-items: center; gap: 10px; }}
.masthead .brand::before {{
  content: ""; width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft);
}}
.eyebrow {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .22em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 18px;
}}
h1.display {{
  font-family: var(--sans);
  font-weight: 700; font-size: clamp(44px, 7.5vw, 84px);
  line-height: 1.02; letter-spacing: -0.025em; margin: 0 0 24px; color: var(--ink);
}}
.lede {{
  font-family: var(--sans);
  font-weight: 400; font-size: 20px; line-height: 1.45;
  color: var(--muted); margin: 0 0 32px; max-width: 56ch;
}}

.chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 32px; }}
.chip {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .04em;
  padding: 5px 10px; border-radius: 999px; border: 1px solid;
  text-transform: lowercase; font-weight: 500; white-space: nowrap;
}}

nav.toc {{ display: flex; flex-wrap: wrap; gap: 0; padding-top: 12px; border-top: 1px solid var(--hairline); }}
nav.toc a {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); text-decoration: none; padding: 12px 16px 12px 0; margin-right: 8px;
  position: relative; transition: color .15s ease;
}}
nav.toc a:hover {{ color: var(--accent); }}
nav.toc a:hover::after {{
  content: ""; position: absolute; left: 0; bottom: 4px;
  width: calc(100% - 16px); height: 1px; background: var(--accent);
}}

section {{ margin: 80px 0; scroll-margin-top: 32px; }}
.section-head {{
  display: grid; grid-template-columns: 80px 1fr; gap: 24px; align-items: baseline;
  margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--hairline);
}}
.section-head .numeral {{
  font-family: var(--serif); font-variation-settings: "opsz" 144;
  font-weight: 300; font-style: italic; font-size: 36px; line-height: 1;
  color: var(--accent); letter-spacing: -.02em;
}}
.section-head .label {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .22em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 6px;
}}
.section-head h2 {{
  font-family: var(--sans);
  font-weight: 700; font-size: 28px; line-height: 1.15; letter-spacing: -.02em;
  margin: 0; color: var(--ink);
}}

.card {{
  background: var(--surface); border: 1px solid var(--hairline); border-radius: 6px;
  padding: 32px 40px; box-shadow: var(--shadow);
}}
/* Wide-bleed section: breaks out of the report container so dense
   tables (e.g. the comparison) get more horizontal room. */
section.bleed {{
  width: min(1240px, calc(100vw - 32px));
  margin-left: 50%;
  transform: translateX(-50%);
}}
.prose {{ max-width: var(--measure); font-size: 16px; line-height: 1.7; color: var(--ink-2); }}
/* Wide variant: removes the comfortable-reading width cap so tables fit. */
.prose.prose-wide {{ max-width: none; }}
.prose.prose-wide table {{ font-size: 13px; }}
.prose.prose-wide td, .prose.prose-wide th {{ padding: 8px 10px; }}
.prose > :first-child {{ margin-top: 0; }}
.prose > :last-child {{ margin-bottom: 0; }}
.prose h1, .prose h2, .prose h4 {{
  font-family: var(--sans); color: var(--ink); letter-spacing: -.015em;
  margin: 32px 0 12px; font-weight: 700; line-height: 1.25;
}}
.prose h1 {{ font-size: 26px; }}
.prose h2 {{ font-size: 20px; }}
.prose h3 {{
  font-size: 16px; font-family: var(--mono); text-transform: uppercase;
  letter-spacing: .14em; color: var(--accent); font-weight: 500; margin: 36px 0 12px;
}}
.prose h4 {{ font-size: 16px; }}
.prose p {{ margin: 0 0 16px; }}
.prose strong {{ color: var(--ink); font-weight: 600; }}
.prose em {{ font-style: italic; color: var(--ink); }}
.prose a {{
  color: var(--accent); text-decoration: none;
  border-bottom: 1px solid var(--accent-soft); transition: border-color .15s ease;
}}
.prose a:hover {{ border-bottom-color: var(--accent); }}
.prose ul, .prose ol {{ margin: 12px 0 20px; padding-left: 24px; }}
.prose li {{ margin: 4px 0; }}
.prose ul li::marker {{ color: var(--accent); }}
.prose blockquote {{
  margin: 20px 0; padding: 4px 0 4px 20px;
  border-left: 2px solid var(--accent);
  font-family: var(--serif); font-style: italic; color: var(--muted); font-size: 18px;
}}
.prose code {{
  font-family: var(--mono); font-size: 13px;
  background: var(--paper-2); padding: 1px 6px; border-radius: 3px; color: var(--ink);
}}
.prose pre {{
  font-family: var(--mono); background: #1a1a1a; color: #f4f0e6;
  padding: 18px 22px; border-radius: 6px; overflow-x: auto;
  font-size: 13px; line-height: 1.6; margin: 20px 0;
}}
.prose pre code {{ background: transparent; color: inherit; padding: 0; }}
.prose img {{
  display: block; max-width: 100%; height: auto;
  border-radius: 4px; border: 1px solid var(--hairline);
  margin: 16px 0; box-shadow: var(--shadow);
}}
.prose table {{
  border-collapse: collapse; width: 100%; font-size: 14px;
  margin: 20px 0; font-variant-numeric: tabular-nums;
}}
.prose th, .prose td {{
  border-bottom: 1px solid var(--hairline); padding: 10px 14px;
  text-align: left; vertical-align: top;
}}
.prose th {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); font-weight: 500; border-bottom: 1px solid var(--rule);
}}
.prose hr {{ border: 0; border-top: 1px solid var(--hairline); margin: 32px 0; }}
.empty {{ color: var(--muted); font-style: italic; }}

/* Journey stream: a vertical sequence of action cards, one per reaction.
   Emotion is conveyed by each card's left-border + step-number-ring color
   and the meta label — no separate chart. */
.journey-stream {{
  display: flex;
  flex-direction: column;
  gap: 16px;
}}
.action-card {{
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-left: 3px solid var(--c, var(--rule));
  border-radius: 0 5px 5px 0;
  padding: 16px 22px 18px;
  box-shadow: var(--shadow);
}}
.action-card .action-head {{
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 10px;
}}
.action-card .step-num {{
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
}}
.action-card .meta {{
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--c, var(--muted));
}}
.action-card .heading {{
  font-family: var(--sans);
  font-size: 18px;
  font-weight: 600;
  line-height: 1.35;
  color: var(--ink);
  margin: 0 0 12px;
  letter-spacing: -.005em;
}}
.action-card .narrative {{
  font-size: 15px;
  line-height: 1.6;
  color: var(--ink-2);
  margin: 0 0 12px;
}}
.action-card .narrative:last-child {{ margin-bottom: 0; }}
.action-card img {{
  display: block;
  max-width: 100%;
  height: auto;
  margin: 14px 0 0;
  border-radius: 4px;
  border: 1px solid var(--hairline);
}}
.action-card .terminal-output {{
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
}}
.action-card .terminal-output code {{
  font-family: inherit;
}}
.action-card .takeaway {{
  margin-top: 14px;
  padding: 10px 14px;
  background: color-mix(in oklab, var(--c, var(--rule)) 6%, transparent);
  border-radius: 3px;
}}
.action-card .takeaway-label {{
  display: inline-block;
  font-family: var(--mono);
  font-size: 9.5px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--c, var(--muted));
  margin-bottom: 3px;
}}
.action-card .takeaway p {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 14px;
  line-height: 1.5;
  color: var(--ink);
  margin: 0;
  font-variation-settings: "opsz" 24;
}}
.strip {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px; margin-top: 8px;
}}
.strip figure {{
  margin: 0; background: var(--surface); border: 1px solid var(--hairline);
  border-radius: 6px; overflow: hidden; box-shadow: var(--shadow);
  transition: transform .2s ease, box-shadow .2s ease;
}}
.strip figure:hover {{
  transform: translateY(-2px);
  box-shadow: 0 1px 0 rgba(23,23,23,.04), 0 12px 28px -10px rgba(23,23,23,.16);
}}
.strip img {{ width: 100%; display: block; aspect-ratio: 16/10; object-fit: cover; background: var(--paper-2); }}
.strip figcaption {{
  font-family: var(--mono); font-size: 11px; letter-spacing: .04em;
  color: var(--muted); padding: 10px 14px; border-top: 1px solid var(--hairline);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}

details.journal {{
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: 6px; box-shadow: var(--shadow); overflow: hidden;
  margin-bottom: 12px;
}}
details.journal:last-child {{ margin-bottom: 0; }}
details.journal > summary {{
  cursor: pointer; list-style: none;
  padding: 18px 24px;
  font-family: var(--mono); font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); display: flex; align-items: center; gap: 12px;
  user-select: none; transition: color .15s ease;
}}
details.journal > summary::-webkit-details-marker {{ display: none; }}
details.journal > summary::before {{
  content: "+"; font-family: var(--serif); font-size: 24px; color: var(--accent);
  line-height: 1; width: 16px; transition: transform .2s ease;
}}
details.journal[open] > summary::before {{ content: "−"; }}
details.journal > summary:hover {{ color: var(--ink); }}
details.journal .body {{ padding: 8px 40px 32px; border-top: 1px solid var(--hairline); }}

footer {{
  margin-top: 96px; padding-top: 24px; border-top: 1px solid var(--hairline);
  font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}}

@media (max-width: 720px) {{
  .report {{ padding: 32px 20px 64px; }}
  h1.display {{ font-size: clamp(40px, 12vw, 64px); }}
  .lede {{ font-size: 18px; }}
  .section-head {{ grid-template-columns: 56px 1fr; gap: 16px; }}
  .section-head .numeral {{ font-size: 28px; }}
  .section-head h2 {{ font-size: 24px; }}
  .card {{ padding: 24px 20px; }}
  details.journal .body {{ padding: 8px 20px 24px; }}
}}

@media print {{
  body {{ background: white; font-size: 11pt; }}
  .report {{ max-width: none; padding: 0; }}
  nav.toc {{ display: none !important; }}
  .card, figure.journey, details.journal, .strip figure {{
    box-shadow: none; border-color: #ddd;
    page-break-inside: avoid; break-inside: avoid;
  }}
  details.journal {{ page-break-inside: auto; }}
  details.journal[open] > summary {{ display: none; }}
  details.journal:not([open]) > summary::after {{ content: " — collapsed in print preview"; }}
  details.journal .body {{ border-top: 0; padding-top: 0; }}
  section {{ margin: 32px 0; }}
  h1.display {{ font-size: 48pt; }}
  a {{ color: black; }}
  .prose a {{ border-bottom-color: #999; }}
  .strip {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>
<main class="report">
  <header class="hero">
    <div class="masthead">
      <div class="brand">Blindspots — User Trial</div>
      <div class="meta">{sub}</div>
    </div>
    <div class="eyebrow">Field notes</div>
    <h1 class="display">{persona_name}</h1>
    <p class="lede">A persona's first encounter with the product, observed and recorded.</p>
    {chips}
    <nav class="toc">{toc_links}</nav>
  </header>

  {journey_section}

  {comparison_section}

  <section id="reference">
    <header class="section-head">
      <div class="numeral">§III</div>
      <div>
        <div class="label">Reference</div>
        <h2>Source artifacts</h2>
      </div>
    </header>
    <details class="journal" id="journal">
      <summary>Exploration journal</summary>
      <div class="body prose">{journal_html}</div>
    </details>
    <details class="journal" id="discovered-specs">
      <summary>Discovered specs</summary>
      <div class="body prose">{specs_html}</div>
    </details>
  </section>

  {screenshots_section}

  <footer>
    <span>Blindspots</span>
    <span>Self-contained · screenshots embedded · {sub}</span>
  </footer>
</main>

</body>
</html>
"""


def render_html(data: TrialData) -> str:
    sub_bits = []
    if data.reactions:
        sub_bits.append(f"{len(data.reactions)} reactions")
    if data.screenshots:
        sub_bits.append(f"{len(data.screenshots)} screenshots")
    sub = " · ".join(sub_bits) if sub_bits else "No artifacts yet"

    toc = []
    if data.reactions:
        toc.append(("#journey", "Journey"))
    if data.comparison_md.strip():
        toc.append(("#comparison", "Comparison"))
    toc.append(("#reference", "Reference"))
    if data.screenshots:
        toc.append(("#screenshots", "Screenshots"))
    toc_links = "".join(f'<a href="{href}">{label}</a>' for href, label in toc)

    journal_html = md_to_html(data.journal_md, data.screenshots)
    journey_spread = render_journey_spread(data.reactions, data.screenshots)
    if journey_spread:
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
    else:
        journey_section = ""

    if data.comparison_md.strip():
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
    else:
        comparison_section = ""

    if data.screenshots:
        screenshots_section = (
            '<section id="screenshots">'
            '<header class="section-head">'
            '<div class="numeral">§IV</div>'
            '<div>'
            '<div class="label">Plates</div>'
            '<h2>Screenshots</h2>'
            '</div>'
            '</header>'
            f"{render_screenshot_strip(data.screenshots)}"
            "</section>"
        )
    else:
        screenshots_section = ""

    return HTML_TEMPLATE.format(
        title=html.escape(f"User Trial — {data.persona_name}"),
        persona_name=html.escape(data.persona_name),
        sub=html.escape(sub),
        chips=render_reaction_chips(data.reactions),
        toc_links=toc_links,
        journey_section=journey_section,
        specs_html=md_to_html(data.specs_md, data.screenshots),
        comparison_section=comparison_section,
        journal_html=journal_html,
        screenshots_section=screenshots_section,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trial_dir", type=Path, help="Path to .blindspots/user-trials/<persona>/")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML path (default: <trial_dir>/report.html)")
    args = parser.parse_args()

    if not args.trial_dir.is_dir():
        print(f"error: {args.trial_dir} is not a directory", file=sys.stderr)
        return 1

    output = args.output or (args.trial_dir / "report.html")

    data = collect_data(args.trial_dir)
    output.write_text(render_html(data), encoding="utf-8")

    size_kb = output.stat().st_size / 1024
    print(
        f"Wrote {output} ({size_kb:.1f} KB · "
        f"{len(data.reactions)} reactions, {len(data.screenshots)} screenshots)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
