# Dogfood Wrap-up and Panel Interview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove PR assumptions from the dogfood cycle, add worktree cleanup and branch-based wrap-up, and add panel interview mode.

**Architecture:** Five markdown files change. The dogfood cycle drops its PR/REVIEW steps for a COMMIT step. The dogfood command adds a wrap-up sequence after the loop. The interview command adds panel mode as the first persona option. No new files created.

**Tech Stack:** Claude Code plugin (markdown command/agent/skill definitions)

---

### Task 1: Dogfood cycle — PR → COMMIT

**Files:**
- Modify: `skills/blindspots/references/dogfood-cycle.md`

- [ ] **Step 1: Replace the PR step with COMMIT**

In `skills/blindspots/references/dogfood-cycle.md`, replace lines 48-54:

```markdown
### PR
1. Create a feature branch: `git checkout -b fix/<descriptive-name>`
2. Commit the changes (spec update + test + fix)
3. Push and open a PR with: what broke (screenshot), the test name, the fix
4. Do NOT merge — leave that for the maintainer

### REVIEW
Check CI and review comments. Address feedback. Repeat until clean.
```

With:

```markdown
### COMMIT
Commit the fix to the worktree branch with a descriptive message.
Do NOT push or open a PR — just commit locally.
```

- [ ] **Step 2: Update the rules line**

In the same file, replace:

```markdown
- **One bug per cycle.** Find one, fix it, PR it, move on.
```

With:

```markdown
- **One bug per cycle.** Find one, fix it, commit it, move on.
```

- [ ] **Step 3: Remove the screenshots-as-evidence rule**

Replace:

```markdown
- **Screenshots as evidence.** Save to `.blindspots/screenshots/` before diagnosing.
```

With:

```markdown
- **Screenshots as evidence.** Save to `.blindspots/screenshots/` when useful.
```

- [ ] **Step 4: Commit**

```bash
git add skills/blindspots/references/dogfood-cycle.md
git commit -m "Replace PR step with commit-only in dogfood cycle"
```

### Task 2: Dogfood command — add wrap-up step

**Files:**
- Modify: `commands/dogfood.md`

- [ ] **Step 1: Update the command description in frontmatter**

Replace:

```yaml
description: Dogfood your product against its specs. Runs a persona-driven testing loop that explores, finds bugs, writes failing tests, fixes code, and opens PRs.
```

With:

```yaml
description: Dogfood your product against its specs. Runs a persona-driven testing loop that explores, finds bugs, fixes code, and commits fixes to a branch.
```

- [ ] **Step 2: Add Step 8: Wrap-up after the Launch step**

After the `## Resolving Specs` section at the end of the file, add:

```markdown
## Step 8: Wrap-up

When the loop ends (user cancels or the cycle exhausts ideas):

1. Clean up the worktree:

```bash
WORKTREE_PATH=".worktrees/$BRANCH"
git worktree remove "$WORKTREE_PATH" 2>/dev/null || true
```

2. Return to the project root (the original working directory before Step 6).

3. Print a summary of the work on the branch:

```bash
echo "## Dogfood summary: $BRANCH"
git log main..$BRANCH --oneline
git diff main..$BRANCH --stat
```

Include a one-line description of each fix from the persona's dogfood journal.

4. Present two options:
   - **Switch to the branch** — run `git checkout $BRANCH` so the user can review changes
   - **Finish the work** — invoke `finishing-a-development-branch` to handle PR, merge, or cleanup

If the branch has no commits (nothing was found/fixed), just clean up the
worktree silently and report that no issues were found.
```

- [ ] **Step 3: Commit**

```bash
git add commands/dogfood.md
git commit -m "Add wrap-up step to dogfood command: cleanup worktree, present options"
```

### Task 3: Interview command — add panel mode

**Files:**
- Modify: `commands/interview.md`

- [ ] **Step 1: Update the arguments description in frontmatter**

Replace:

```yaml
description: "--persona <name> to skip selection, --context <user-trial|experiment-name> to skip context prompt"
```

With:

```yaml
description: "--persona <name|panel> to skip selection, --context <user-trial|experiment-name> to skip context prompt"
```

- [ ] **Step 2: Add panel option to Step 2: Select Persona**

Replace the current Step 2 content:

```markdown
## Step 2: Select Persona

If `--persona <name>` given, substring match against `.blindspots/personas.md`.

Otherwise, present the available personas and ask the user to pick one:

- List each persona's name and quote (exclude the anti-persona)
- Ask: "Who would you like to interview?"

Print the selected persona's name, quote, and background.
```

With:

```markdown
## Step 2: Select Persona

If `--persona panel` given, skip to panel mode (see Step 2b).

If `--persona <name>` given, substring match against `.blindspots/personas.md`.

Otherwise, present the available personas and ask the user to pick one:

- **Panel — all personas react to your question at once** (first option, always available)
- Each persona's name and quote (exclude the anti-persona)
- Ask: "Who would you like to interview?"

If a single persona is selected, print their name, quote, and background.

### Step 2b: Panel Mode

When panel is selected:

- Skip Step 3 (context selection) — panel mode is always fresh context
- Skip Step 4 (agent launch) — panel runs inline, not as a subagent
- Go directly to Step 5: Panel Interview

Print: "Panel mode — all personas will respond to each question."
```

- [ ] **Step 3: Add Step 5: Panel Interview**

After the current Step 4 (Launch), add:

```markdown
## Step 5: Panel Interview

Panel mode runs inline in the main session. For each user message:

1. Each persona (excluding the anti-persona) responds with 2-4 sentences
   in character, presented under their name and quote:

   ```
   **Priya — The Shipping Solo Dev**
   > "I don't have a QA team. I have a deploy button and a prayer."

   [2-4 sentence response in Priya's voice]

   **Marcus — The Skeptical Staff Engineer**
   > "Show me a tool that finds real bugs..."

   [2-4 sentence response in Marcus's voice]

   ...
   ```

2. Wait for the user's next question. Repeat until the user ends the session.

3. Save the full panel transcript to
   `.blindspots/interviews/panel-<timestamp>.md` with a header listing all
   participating personas and the date.
```

- [ ] **Step 4: Commit**

```bash
git add commands/interview.md
git commit -m "Add panel interview mode: all personas respond to each question"
```

### Task 4: Update SKILL.md

**Files:**
- Modify: `skills/blindspots/SKILL.md`

- [ ] **Step 1: Fix the config table**

Replace:

```markdown
| `.blindspots/config.md` | Project testing config (setup, URL, explore, diagnose, test, specs) |
```

With:

```markdown
| `.blindspots/config.md` | Project testing config (setup, start, explore, diagnose, test, specs) |
```

(Note: this may already be fixed from the dogfood session — check before editing.)

- [ ] **Step 2: Update the dogfood cycle description in Reference Files**

Replace:

```markdown
- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → DIAGNOSE → RED → GREEN → PR)
```

With:

```markdown
- **`references/dogfood-cycle.md`** — Guided testing cycle (EXPLORE → USE → DIAGNOSE → FIX → COMMIT)
```

- [ ] **Step 3: Update the shared steps persona selection**

Check whether the shared steps already describe per-command persona selection
(this may have been fixed in the dogfood session). If not, update step 3 to
note that `/interview` supports panel mode:

```markdown
3. Select persona — method varies by command:
   - `/dogfood`, `/user-trial`: random, or `--persona <name>`
   - `/interview`: shows persona list with panel option, asks user to pick
   - `/experiment`: prompts interactively (test name, variants, user type, run count)
```

- [ ] **Step 4: Commit**

```bash
git add skills/blindspots/SKILL.md
git commit -m "Update SKILL.md: dogfood cycle description, panel interview"
```

### Task 5: Final review

- [ ] **Step 1: Verify dogfood-cycle.md has no PR/push/gh references**

```bash
grep -i "PR\|push\|pull request\|gh " skills/blindspots/references/dogfood-cycle.md
```

Expected: no matches (except possibly "PR" in unrelated context).

- [ ] **Step 2: Verify interview.md has panel mode**

```bash
grep -i "panel" commands/interview.md
```

Expected: matches for panel mode steps.

- [ ] **Step 3: Verify dogfood.md has wrap-up step**

```bash
grep -i "wrap-up\|worktree remove\|finishing" commands/dogfood.md
```

Expected: matches for the wrap-up sequence.

- [ ] **Step 4: Commit any remaining changes**

If any fixes were needed, commit them:

```bash
git add -A
git commit -m "Fix issues found during review"
```
