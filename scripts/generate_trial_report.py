#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown>=3.5"]
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

import markdown


REACTION_SCORES = {
    "delight": 5,
    "surprise": 4,
    "indifference": 3,
    "confusion": 2,
    "frustration": 1,
    "anxiety": 1,
}

REACTION_COLORS = {
    "delight": "#16a34a",
    "surprise": "#0891b2",
    "indifference": "#737373",
    "confusion": "#d97706",
    "frustration": "#dc2626",
    "anxiety": "#7c3aed",
}


@dataclass
class Reaction:
    title: str
    reaction: str
    what_happened: str
    why_matters: str = ""
    screenshot: str | None = None


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

        def grab(field_name: str) -> str:
            m = re.search(
                rf"^\s*[-*]\s*\*\*{re.escape(field_name)}\*\*\s*:\s*(.+)$",
                body,
                re.MULTILINE | re.IGNORECASE,
            )
            return m.group(1).strip() if m else ""

        reaction_word = grab("Reaction").lower()
        # Take the first recognized word if the line is a list of options.
        for word in REACTION_SCORES:
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
                what_happened=grab("What happened"),
                why_matters=grab("Why it matters"),
                screenshot=screenshot,
            )
        )
    return reactions


def sanitize_journey_label(text: str, max_len: int = 60) -> str:
    """Mermaid `journey` parses `:` and `,` as separators. Strip them."""
    cleaned = text.replace(":", "—").replace(",", ";").replace("\n", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def build_mermaid_journey(persona: str, reactions: list[Reaction]) -> str:
    if not reactions:
        return ""
    lines = ["journey", f"    title {sanitize_journey_label(persona)}'s trial"]
    lines.append("    section Session")
    actor = sanitize_journey_label(persona, max_len=20) or "User"
    for r in reactions:
        label = sanitize_journey_label(r.what_happened or r.title) or "(unlabeled)"
        score = REACTION_SCORES.get(r.reaction, 3)
        lines.append(f"      {label}: {score}: {actor}")
    return "\n".join(lines)


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
        output_format="html5",
    )
    return rewrite_image_refs(body, screenshots)


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
<style>
:root {{
  --bg: #0b0d10;
  --panel: #14181d;
  --panel-2: #1b2027;
  --text: #e7ecef;
  --muted: #9aa4ad;
  --accent: #7dd3fc;
  --border: #232a32;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
  font-size: 15px;
}}
.shell {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 80px; }}
header.hero {{ padding: 24px 0 32px; border-bottom: 1px solid var(--border); margin-bottom: 32px; }}
header.hero .eyebrow {{ font-size: 12px; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); }}
header.hero h1 {{ font-size: 32px; margin: 8px 0 4px; font-weight: 700; }}
header.hero .sub {{ color: var(--muted); }}
nav.toc {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 20px 0 0; }}
nav.toc a {{
  font-size: 13px; color: var(--muted); text-decoration: none;
  padding: 6px 12px; border: 1px solid var(--border); border-radius: 999px;
  background: var(--panel);
}}
nav.toc a:hover {{ color: var(--text); border-color: var(--accent); }}
section {{ margin: 40px 0; }}
section > h2 {{
  font-size: 20px; margin: 0 0 16px;
  display: flex; align-items: center; gap: 10px;
}}
section > h2::before {{
  content: ""; width: 4px; height: 18px; background: var(--accent); border-radius: 2px;
}}
.card {{
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 20px 24px;
}}
.card.markdown :is(h1,h2,h3,h4) {{ margin-top: 28px; margin-bottom: 8px; }}
.card.markdown h1 {{ font-size: 22px; }}
.card.markdown h2 {{ font-size: 18px; color: var(--accent); }}
.card.markdown h3 {{ font-size: 16px; }}
.card.markdown code {{
  background: var(--panel-2); padding: 2px 6px; border-radius: 4px;
  font-size: 13px;
}}
.card.markdown pre {{
  background: var(--panel-2); padding: 14px 16px; border-radius: 8px;
  overflow-x: auto; border: 1px solid var(--border);
}}
.card.markdown pre code {{ background: transparent; padding: 0; }}
.card.markdown img {{ max-width: 100%; border-radius: 8px; border: 1px solid var(--border); margin: 8px 0; }}
.card.markdown blockquote {{
  border-left: 3px solid var(--accent); padding-left: 14px; color: var(--muted); margin: 8px 0;
}}
.card.markdown table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
.card.markdown th, .card.markdown td {{ border: 1px solid var(--border); padding: 6px 10px; text-align: left; }}
.card.markdown ul, .card.markdown ol {{ padding-left: 22px; }}
.empty {{ color: var(--muted); font-style: italic; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 16px; }}
.chip {{
  font-size: 12px; padding: 4px 10px; border-radius: 999px;
  border: 1px solid; text-transform: lowercase; font-weight: 500;
}}
.strip {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px; margin-top: 16px;
}}
.strip figure {{ margin: 0; background: var(--panel-2); border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
.strip img {{ width: 100%; display: block; aspect-ratio: 16/10; object-fit: cover; }}
.strip figcaption {{
  font-size: 11px; color: var(--muted); padding: 6px 8px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.mermaid-wrap {{
  background: white; padding: 24px; border-radius: 10px;
  border: 1px solid var(--border); overflow-x: auto;
}}
.mermaid-fallback {{
  color: var(--muted); font-size: 13px; padding: 12px 0 0;
  border-top: 1px solid var(--border); margin-top: 16px;
}}
details summary {{ cursor: pointer; color: var(--accent); user-select: none; padding: 4px 0; }}
footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; }}
@media print {{
  body {{ background: white; color: black; }}
  .card, .mermaid-wrap, nav.toc a {{ background: white; border-color: #ccc; color: black; }}
}}
</style>
</head>
<body>
<div class="shell">
  <header class="hero">
    <div class="eyebrow">Blindspots · User Trial</div>
    <h1>{persona_name}</h1>
    <div class="sub">{sub}</div>
    {chips}
    <nav class="toc">
      {toc_links}
    </nav>
  </header>

  {journey_section}

  <section id="discovered-specs">
    <h2>Discovered Specs</h2>
    <div class="card markdown">{specs_html}</div>
  </section>

  <section id="reactions">
    <h2>Reactions</h2>
    <div class="card markdown">{reactions_html}</div>
  </section>

  {comparison_section}

  <section id="journal">
    <h2>Exploration Journal</h2>
    <details>
      <summary>Show full journal</summary>
      <div class="card markdown" style="margin-top:12px">{journal_html}</div>
    </details>
  </section>

  {screenshots_section}

  <footer>
    Generated by blindspots · self-contained HTML, screenshots embedded as data URIs.
  </footer>
</div>

{mermaid_script}
</body>
</html>
"""


MERMAID_SCRIPT = """<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'loose' });
  } else {
    document.querySelectorAll('.mermaid').forEach(function (el) {
      el.style.display = 'none';
    });
    var note = document.querySelector('.mermaid-fallback');
    if (note) note.style.display = 'block';
  }
</script>
"""


def render_html(data: TrialData) -> str:
    journey_src = build_mermaid_journey(data.persona_name, data.reactions)

    sub_bits = []
    if data.reactions:
        sub_bits.append(f"{len(data.reactions)} reactions")
    if data.screenshots:
        sub_bits.append(f"{len(data.screenshots)} screenshots")
    sub = " · ".join(sub_bits) if sub_bits else "No artifacts yet"

    toc = [
        ("#journey", "Journey"),
        ("#discovered-specs", "Discovered Specs"),
        ("#reactions", "Reactions"),
        ("#comparison", "Comparison"),
        ("#journal", "Journal"),
        ("#screenshots", "Screenshots"),
    ]
    toc_links = "".join(f'<a href="{href}">{label}</a>' for href, label in toc)

    if journey_src:
        journey_section = (
            '<section id="journey">'
            "<h2>User Journey</h2>"
            '<div class="mermaid-wrap">'
            f'<pre class="mermaid">{html.escape(journey_src)}</pre>'
            '<div class="mermaid-fallback" style="display:none">'
            "Mermaid CDN unavailable. Open this file with internet access to see the journey diagram, "
            "or paste the source below into <a href='https://mermaid.live'>mermaid.live</a>:"
            f'<pre style="white-space:pre-wrap">{html.escape(journey_src)}</pre>'
            "</div></div></section>"
        )
    else:
        journey_section = ""

    if data.comparison_md.strip():
        comparison_section = (
            '<section id="comparison">'
            "<h2>Comparison vs Actual Specs</h2>"
            f'<div class="card markdown">{md_to_html(data.comparison_md, data.screenshots)}</div>'
            "</section>"
        )
    else:
        comparison_section = ""

    if data.screenshots:
        screenshots_section = (
            '<section id="screenshots">'
            "<h2>Screenshots</h2>"
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
        reactions_html=md_to_html(data.reactions_md, data.screenshots),
        comparison_section=comparison_section,
        journal_html=md_to_html(data.journal_md, data.screenshots),
        screenshots_section=screenshots_section,
        mermaid_script=MERMAID_SCRIPT,
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
