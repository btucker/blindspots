#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Shakeout — Exploratory Testing Loop.

Usage:
    shakeout.py                            # run in current directory
    shakeout.py --project ~/projects/x     # run against a specific project
    shakeout.py --blind --project ~/x      # blind discovery mode
    shakeout.py --fresh                    # force a fresh session
    shakeout.py --setup                    # just set up
    shakeout.py --teardown                 # just tear down
"""

import argparse
import os
import random
import re
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shakeout — Exploratory Testing Loop")
    parser.add_argument("project", nargs="?", default=None, help="Project directory")
    parser.add_argument("--project", dest="project_flag", default=None, help="Project directory")
    parser.add_argument("--blind", action="store_true", help="Blind discovery mode (no specs)")
    parser.add_argument("--persona", default=None, help="Persona name (random if omitted)")
    parser.add_argument("--fresh", action="store_true", help="Force a fresh session")
    parser.add_argument("--setup", action="store_true", help="Just set up")
    parser.add_argument("--teardown", action="store_true", help="Just tear down")
    args = parser.parse_args()
    args.project_dir = Path(args.project_flag or args.project or os.getcwd()).expanduser().resolve()
    return args


def extract_code_block(md: str, heading: str) -> str:
    """Extract the first fenced code block under a ## heading."""
    in_section = False
    in_fence = False
    lines: list[str] = []
    for line in md.splitlines():
        if re.match(rf"^## {re.escape(heading)}\b", line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("```"):
            if in_fence:
                break
            in_fence = True
            continue
        if in_section and in_fence:
            lines.append(line)
    return "\n".join(lines)


def extract_section(md: str, heading: str) -> str:
    """Extract all text under a ## heading until the next ## heading."""
    in_section = False
    lines: list[str] = []
    for line in md.splitlines():
        if re.match(rf"^## {re.escape(heading)}\b", line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            lines.append(line)
    return "\n".join(lines).strip()


def extract_url(md: str) -> str:
    """Extract the URL from ## URL section (first non-empty line after heading)."""
    text = extract_section(md, "URL")
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return "http://localhost:3000"


def load_personas(project_dir: Path) -> dict[str, str]:
    """Load personas from SHAKEOUT-PERSONAS.md. Returns {name: description}."""
    path = project_dir / "SHAKEOUT-PERSONAS.md"
    if not path.exists():
        return {}
    personas: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            if current_name:
                personas[current_name] = "\n".join(current_lines).strip()
            current_name = line[3:].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name:
        personas[current_name] = "\n".join(current_lines).strip()
    return personas


def select_persona(
    project_dir: Path, shakeout_md: str, name: str | None = None,
) -> tuple[str, str]:
    """Select a persona. Returns (name, description).

    Priority: named match > random from file > inline ## Persona > generic fallback.
    """
    personas = load_personas(project_dir)

    if name:
        for pname, pdesc in personas.items():
            if name.lower() in pname.lower():
                return pname, pdesc
        available = ", ".join(personas) or "(none — no SHAKEOUT-PERSONAS.md)"
        sys.exit(f"Error: persona '{name}' not found. Available: {available}")

    if personas:
        pname = random.choice(list(personas.keys()))
        return pname, personas[pname]

    inline = extract_section(shakeout_md, "Persona")
    if inline:
        return "Default", inline

    return "Default", "You are a first-time user exploring this product."


def read_env(envfile: Path) -> dict[str, str]:
    env = {}
    if envfile.exists():
        for line in envfile.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


def write_env(envfile: Path, env: dict[str, str]) -> None:
    envfile.write_text("\n".join(f"{k}={v}" for k, v in env.items()) + "\n")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def git(*args: str, cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess:
    return run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


def resolve_base_ref(project_dir: Path) -> str:
    for ref in ("origin/main", "main", "HEAD"):
        r = git("rev-parse", "--verify", ref, cwd=project_dir)
        if r.returncode == 0:
            return r.stdout.strip()
    sys.exit("Error: could not resolve a base ref (tried origin/main, main, HEAD)")


def teardown(envfile: Path, statefile: Path) -> None:
    if envfile.exists():
        env = read_env(envfile)
        pid = env.get("SHAKEOUT_DEV_PID")
        if pid:
            print(f"Stopping dev server (PID {pid})...")
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        envfile.unlink()
    if statefile.exists():
        statefile.unlink()
    print("Teardown complete.")


def gather_project_context(project_dir: Path, shakeout_md: str) -> str:
    """Gather project files to feed persona generation."""
    parts: list[str] = []

    # Always include SHAKEOUT.md
    parts.append(f"## SHAKEOUT.md\n\n{shakeout_md}")

    # Try common context files
    for name in ("README.md", "package.json"):
        path = project_dir / name
        if path.exists():
            content = path.read_text()[:5000]
            parts.append(f"## {name}\n\n{content}")

    # Include specs if referenced
    specs_rel = extract_section(shakeout_md, "Specs").strip()
    if specs_rel:
        specs_path = project_dir / specs_rel
        if specs_path.exists():
            content = specs_path.read_text()[:8000]
            parts.append(f"## {specs_rel}\n\n{content}")

    return "\n\n---\n\n".join(parts)


def generate_personas(project_dir: Path, shakeout_md: str) -> None:
    """Use Claude to generate SHAKEOUT-PERSONAS.md based on project context."""
    personas_path = project_dir / "SHAKEOUT-PERSONAS.md"
    if personas_path.exists():
        return

    print("Generating personas...")
    context = gather_project_context(project_dir, shakeout_md)

    prompt = f"""\
Based on the project context below, generate 5-6 user personas for exploratory testing.

Each persona should:
- Be a realistic user of THIS specific product (not generic)
- Have a distinct background, goal, and behavior pattern
- Test different aspects of the product (some patient, some rushed, some technical, \
some non-technical, some with accessibility needs, some on mobile)
- Be written in second person ("You are...")
- Include personality traits that affect HOW they use the product (click patterns, \
patience level, what they notice, what they skip)
- Be 3-5 sentences

---

{context}"""

    result = run(
        [
            "claude", "--print",
            "--output-format", "text",
            "--system-prompt", (
                "You generate markdown files. Output ONLY the file content, "
                "no commentary, no preamble, no code fences. "
                "Start with `# Shakeout Personas` and use `## Name` for each persona."
            ),
            prompt,
        ],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip():
        output = result.stdout.strip()
        personas_path.write_text(output + "\n")
        count = len(re.findall(r"^## ", output, re.MULTILINE))
        print(f"Generated {count} personas → SHAKEOUT-PERSONAS.md")
    else:
        print("Warning: could not generate personas. Create SHAKEOUT-PERSONAS.md manually.")


def setup(project_dir: Path, envfile: Path, shakeout_md: str) -> None:
    project_name = project_dir.name
    print(f"=== Setting up {project_name} ===")

    setup_cmd = extract_code_block(shakeout_md, "Setup")
    if setup_cmd:
        print("Running setup from SHAKEOUT.md...")
        run(["bash", "-c", setup_cmd], cwd=project_dir, check=True)
    else:
        print("No setup command found in SHAKEOUT.md. Skipping.")

    generate_personas(project_dir, shakeout_md)

    web_url = extract_url(shakeout_md)
    write_env(envfile, {
        "SHAKEOUT_WEB_URL": web_url,
        "SHAKEOUT_PROJECT_DIR": str(project_dir),
    })
    print(f"Setup complete. URL: {web_url}")


def create_worktree(project_dir: Path, prefix: str = "shakeout") -> Path:
    git("fetch", "origin", cwd=project_dir)
    branch = f"{prefix}/{datetime.now():%Y%m%d-%H%M%S}"
    worktree_dir = project_dir / ".worktrees" / branch
    worktree_dir.parent.mkdir(parents=True, exist_ok=True)
    base_ref = resolve_base_ref(project_dir)
    git("worktree", "add", str(worktree_dir), "-b", branch, base_ref, cwd=project_dir, check=True)
    return worktree_dir


def build_guided_system_prompt(
    project_dir: Path, web_url: str, shakeout_md: str,
    persona_name: str, persona_desc: str,
) -> str:
    return f"""\
You are running a shakeout — an exploratory testing session for the project "{project_dir.name}".

## Your Persona: {persona_name}

{persona_desc}

Stay in character throughout the session. Your persona shapes how you explore, \
what you notice, and what frustrates you.

## Environment

Your working directory is an isolated git worktree. The app is running at {web_url}.

Below is the project's SHAKEOUT.md, which defines what to explore, how to diagnose \
issues, and how to write tests. Use it alongside the cycle instructions you receive \
in each loop iteration.

---

{shakeout_md}"""


def build_blind_system_prompt(
    project_dir: Path, web_url: str, shakeout_md: str,
    persona_name: str, persona_desc: str,
) -> str:
    infra_sections = "\n\n".join(
        f"## {heading}\n\n{text}"
        for heading in ("Setup", "URL", "Test")
        if (text := extract_section(shakeout_md, heading))
    )
    return f"""\
You are running a blind shakeout — an exploratory testing session for "{project_dir.name}".

## Your Persona: {persona_name}

{persona_desc}

Stay in character throughout the session. Your persona shapes how you explore, \
what you notice, and what frustrates you.

## Mission

You have NO access to specs, requirements, or documentation. Your job is to explore \
the product as a first-time user, discover what it does, and write specifications \
based purely on what you observe.

Write your discovered specs to `shakeout-discovered-specs.md` in your working \
directory. Use EARS format with IDs (DISC-1, DISC-2, etc.).

## Environment

Your working directory is an isolated git worktree. The app is running at {web_url}.

IMPORTANT: Do NOT read any spec files, design docs, requirements, READMEs, or \
AGENTS.md in this project. You must discover behavior only through the UI.

---

{infra_sections}"""


def run_comparison(
    worktree_dir: Path, project_dir: Path, shakeout_md: str,
) -> None:
    discovered_path = worktree_dir / "shakeout-discovered-specs.md"
    if not discovered_path.exists():
        print("No discovered specs found — skipping comparison.")
        return

    specs_rel = extract_section(shakeout_md, "Specs").strip()
    if not specs_rel:
        print("No ## Specs section in SHAKEOUT.md — skipping comparison.")
        return

    specs_path = project_dir / specs_rel
    if not specs_path.exists():
        print(f"Specs file not found: {specs_path} — skipping comparison.")
        return

    print()
    print("=== Running spec comparison ===")

    compare_instructions = (SCRIPT_DIR / "compare-prompt.md").read_text()
    discovered_text = discovered_path.read_text()
    actual_text = specs_path.read_text()

    prompt = f"""{compare_instructions}

---

## Discovered Specs (from blind exploration)

{discovered_text}

---

## Actual Specs (from project documentation)

{actual_text}"""

    result = run(
        ["claude", "--print", prompt],
        cwd=worktree_dir,
        capture_output=True,
        text=True,
    )

    report = result.stdout
    report_path = worktree_dir / "shakeout-comparison.md"
    report_path.write_text(report)

    print(f"Comparison written to: {report_path}")
    print()
    print(report)


def launch_claude(
    worktree_dir: Path, web_url: str, project_dir: Path,
    system_prompt: str, loop_prompt: str, *, replace_process: bool = True,
) -> None:
    base_cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--chrome",
        "--append-system-prompt", system_prompt,
    ]

    settings_file = worktree_dir / ".claude" / "settings.local.json"
    if settings_file.exists():
        cmd = [*base_cmd, "--continue"]
    else:
        cmd = [*base_cmd, f"/loop 10m {loop_prompt}"]

    os.chdir(worktree_dir)
    os.environ["SHAKEOUT_WEB_URL"] = web_url
    os.environ["SHAKEOUT_PROJECT_DIR"] = str(project_dir)

    if replace_process:
        os.execvp("claude", cmd)
    else:
        run(cmd)


def main() -> None:
    args = parse_args()
    project_dir = args.project_dir

    shakeout_md_path = project_dir / "SHAKEOUT.md"
    if not shakeout_md_path.exists():
        print(f"Error: No SHAKEOUT.md found in {project_dir}")
        print("Create a SHAKEOUT.md with project-specific testing instructions.")
        print(f"See: {SCRIPT_DIR / 'README.md'}")
        sys.exit(1)

    shakeout_md = shakeout_md_path.read_text()
    envfile = project_dir / ".shakeout-env"
    statefile = project_dir / ".shakeout-state"

    # ── Teardown ──────────────────────────────────────────────────────
    if args.teardown:
        teardown(envfile, statefile)
        return

    # ── Fresh ─────────────────────────────────────────────────────────
    if args.fresh:
        statefile.unlink(missing_ok=True)

    # ── Resume previous worktree ──────────────────────────────────────
    worktree_dir: Path | None = None
    if statefile.exists():
        state = read_env(statefile)
        prev = state.get("WORKTREE_DIR", "")
        if prev and Path(prev).is_dir():
            worktree_dir = Path(prev)
            print("=== Resuming in previous worktree ===")
            print(f"Worktree: {worktree_dir}")
        else:
            print("Previous worktree gone, starting fresh.")
            statefile.unlink(missing_ok=True)

    # ── Setup ─────────────────────────────────────────────────────────
    if not envfile.exists():
        setup(project_dir, envfile, shakeout_md)
    else:
        print("Already set up (run --teardown to reset).")

    env = read_env(envfile)
    web_url = env.get("SHAKEOUT_WEB_URL", "http://localhost:3000")

    if args.setup:
        return

    # ── Create worktree ───────────────────────────────────────────────
    prefix = "shakeout-blind" if args.blind else "shakeout"
    if worktree_dir is None:
        worktree_dir = create_worktree(project_dir, prefix=prefix)

    statefile.write_text(f"WORKTREE_DIR={worktree_dir}\n")

    mode_label = "Blind Shakeout" if args.blind else "Shakeout"
    print()
    print(f"=== Starting {mode_label}: {project_dir.name} ===")
    print(f"Worktree: {worktree_dir}")
    print(f"Web URL:  {web_url}")
    print()

    # ── Persona ────────────────────────────────────────────────────────
    persona_name, persona_desc = select_persona(project_dir, shakeout_md, args.persona)
    print(f"Persona:  {persona_name}")
    print()

    # ── Launch ────────────────────────────────────────────────────────
    if args.blind:
        system_prompt = build_blind_system_prompt(
            project_dir, web_url, shakeout_md, persona_name, persona_desc,
        )
        loop_prompt = (SCRIPT_DIR / "blind-prompt.md").read_text()

        launch_claude(
            worktree_dir, web_url, project_dir,
            system_prompt, loop_prompt, replace_process=False,
        )

        run_comparison(worktree_dir, project_dir, shakeout_md)
    else:
        system_prompt = build_guided_system_prompt(
            project_dir, web_url, shakeout_md, persona_name, persona_desc,
        )
        loop_prompt = (SCRIPT_DIR / "prompt.md").read_text()

        launch_claude(
            worktree_dir, web_url, project_dir,
            system_prompt, loop_prompt, replace_process=True,
        )


if __name__ == "__main__":
    main()
