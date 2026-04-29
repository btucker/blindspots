# Trial Report Curation Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a post-generation curation pass to the user-trial workflow so the final HTML report tells the story of the persona's experience as clearly as possible.

**Architecture:** This is a command-instruction change, not a report generator change. Update `commands/user-trial.md` Step 8 so `generate_trial_report.py` is treated as producing a first draft, then instruct the agent to inspect and improve the final artifact using judgement. Also correct the stale Step 8 description that still references Mermaid, because the current generator now renders vertical action cards.

**Tech Stack:** Markdown command definition for the Blindspots plugin workflow.

---

## File Structure

- Modify: `commands/user-trial.md`
  - Add post-generation curation instructions.
  - Update stale generated-report description from Mermaid journey language to the current HTML report layout.
  - Keep the `uv` command unchanged.

## Scope Notes

- Do not modify `scripts/generate_trial_report.py` for this change. The generator already supports the redesigned report; this plan only changes the workflow that runs it.
- Do not add a rigid checklist that prevents judgement. The point is to make the final report stronger, not to make the agent mechanically validate boxes.
- Preserve the user's phrasing: the curation pass should make the report "tell the story of the persona's experience."

### Task 1: Add Curation Pass To User Trial Report Step

**Files:**
- Modify: `commands/user-trial.md`

- [ ] **Step 1: Read the current Step 8**

Run:

```bash
sed -n '120,150p' commands/user-trial.md
```

Expected: Step 8 contains the `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/generate_trial_report.py"` command and currently describes a Mermaid journey diagram.

- [ ] **Step 2: Replace the stale report description**

In `commands/user-trial.md`, replace:

```markdown
The script reads `journal.md`, `discovered-specs.md`, `reactions.md`, and
`comparison.md` (whichever exist), embeds every PNG/JPG from `screenshots/`
as base64 `data:` URIs, and renders a Mermaid `journey` diagram from the
ordered reactions. Output: `.blindspots/user-trials/<persona-slug>/report.html`.

The file is single-file shareable — just attach it. Mermaid loads from CDN at
view time; offline viewers get a fallback note with the raw diagram source.
```

With:

```markdown
The script reads `journal.md`, `discovered-specs.md`, `reactions.md`, and
`comparison.md` (whichever exist), embeds every PNG/JPG from `screenshots/`
as base64 `data:` URIs, renders the persona journey as vertical action cards,
and folds reference artifacts below the comparison. Output:
`.blindspots/user-trials/<persona-slug>/report.html`.

The file is single-file shareable — just attach it.
```

- [ ] **Step 3: Add the curation pass**

Immediately after the generated-report description from Step 2, add:

```markdown
After generating `report.html`, inspect the rendered report before presenting it.

Treat the script output as a first draft. Make a curation pass so the final
report tells the story of the persona's experience as clearly as possible.

Use judgement to:
- strengthen the narrative flow from first encounter to final impression
- tighten headings, captions, takeaways, and section emphasis
- improve evidence placement so screenshots or terminal output support the
  moment they belong to
- fix awkward tables, spacing, or layout issues that interrupt the story
- preserve uncertainty and evidence; do not invent findings or make the persona
  sound more certain than the trial supports

Prefer editing source artifacts or the generator when the improvement should
apply to future reports. Directly polish `report.html` when that is the fastest
way to make this specific report stronger.
```

- [ ] **Step 4: Verify the command text includes the new north star**

Run:

```bash
rg -n "tells the story of the persona's experience|Treat the script output as a first draft|Mermaid|single-file shareable" commands/user-trial.md
```

Expected:
- Matches for `Treat the script output as a first draft`
- Match for `tells the story of the persona's experience`
- Match for `single-file shareable`
- No `Mermaid` match

- [ ] **Step 5: Review the Step 8 excerpt**

Run:

```bash
sed -n '120,165p' commands/user-trial.md
```

Expected: Step 8 reads naturally in this order:

1. Generate the report with `uv`.
2. Describe what the script produces.
3. Curate the generated report.
4. Handle missing `uv`.

- [ ] **Step 6: Commit**

```bash
git add commands/user-trial.md
git commit -m "Add curation pass to trial report workflow"
```

### Task 2: Final Verification

**Files:**
- Read: `commands/user-trial.md`

- [ ] **Step 1: Confirm only the intended workflow file changed**

Run:

```bash
git diff --stat HEAD~1..HEAD
```

Expected: only `commands/user-trial.md` changed.

- [ ] **Step 2: Confirm report generation command is unchanged**

Run:

```bash
rg -n 'uv run "\$\{CLAUDE_PLUGIN_ROOT\}/scripts/generate_trial_report.py"|\.blindspots/user-trials/<persona-slug>/' commands/user-trial.md
```

Expected: the existing generator invocation and output directory references are still present.

- [ ] **Step 3: Confirm the old Mermaid description is gone**

Run:

```bash
rg -n "Mermaid|journey diagram|offline viewers" commands/user-trial.md
```

Expected: no matches.

- [ ] **Step 4: Confirm curation guardrails are present**

Run:

```bash
rg -n "do not invent findings|Directly polish `report.html`|first encounter to final impression" commands/user-trial.md
```

Expected: all three phrases match.
