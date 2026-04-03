#!/usr/bin/env bash
set -euo pipefail

# Shakeout — Exploratory Testing Loop
#
# Usage:
#   shakeout.sh                        # run in current directory
#   shakeout.sh --project ~/projects/x # run against a specific project
#   shakeout.sh --fresh                # force a fresh session
#   shakeout.sh --setup                # just set up
#   shakeout.sh --teardown             # just tear down

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse args
PROJECT_DIR=""
ACTION="run"
while [ $# -gt 0 ]; do
    case "$1" in
        --project)  shift; PROJECT_DIR="$1" ;;
        --fresh)    ACTION="fresh" ;;
        --setup)    ACTION="setup" ;;
        --teardown) ACTION="teardown" ;;
        run)        ACTION="run" ;;
        *)
            if [ -z "$PROJECT_DIR" ] && [ -d "$1" ]; then
                PROJECT_DIR="$1"
            else
                echo "Usage: $0 [--project <path>] [--fresh|--setup|--teardown]"
                exit 1
            fi
            ;;
    esac
    shift
done

# Default to current directory
if [ -z "$PROJECT_DIR" ]; then
    PROJECT_DIR="$(pwd)"
fi
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

# Verify SHAKEOUT.md exists
if [ ! -f "$PROJECT_DIR/SHAKEOUT.md" ]; then
    echo "Error: No SHAKEOUT.md found in $PROJECT_DIR"
    echo "Create a SHAKEOUT.md with project-specific testing instructions."
    echo "See: $SCRIPT_DIR/README.md"
    exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_DIR")
ENVFILE="$PROJECT_DIR/.shakeout-env"
STATEFILE="$PROJECT_DIR/.shakeout-state"

# ── Teardown ────────────────────────────────────────────────────────────
if [ "$ACTION" = "teardown" ]; then
    if [ -f "$ENVFILE" ]; then
        source "$ENVFILE"
        if [ -n "${SHAKEOUT_DEV_PID:-}" ]; then
            echo "Stopping dev server (PID $SHAKEOUT_DEV_PID)..."
            kill "$SHAKEOUT_DEV_PID" 2>/dev/null || true
        fi
        rm -f "$ENVFILE"
    fi
    rm -f "$STATEFILE"
    echo "Teardown complete."
    exit 0
fi

# ── Fresh ───────────────────────────────────────────────────────────────
if [ "$ACTION" = "fresh" ]; then
    rm -f "$STATEFILE"
fi

# ── Check for previous worktree ─────────────────────────────────────────
WORKTREE_DIR=""
if [ -f "$STATEFILE" ]; then
    source "$STATEFILE"
    if [ -n "$WORKTREE_DIR" ] && [ -d "$WORKTREE_DIR" ]; then
        echo "=== Resuming in previous worktree ==="
        echo "Worktree: $WORKTREE_DIR"
    else
        echo "Previous worktree gone, starting fresh."
        WORKTREE_DIR=""
        rm -f "$STATEFILE"
    fi
fi

# ── Setup dev server ────────────────────────────────────────────────────
if [ ! -f "$ENVFILE" ]; then
    echo "=== Setting up $PROJECT_NAME ==="

    # Extract setup command from SHAKEOUT.md
    # Looks for a fenced code block after "## Setup"
    SETUP_CMD=$(awk '/^## Setup/{found=1;next} found&&/^## /{exit} found&&/^```/{fence=!fence;next} found&&fence{print}' "$PROJECT_DIR/SHAKEOUT.md" | head -20)

    if [ -n "$SETUP_CMD" ]; then
        echo "Running setup from SHAKEOUT.md..."
        cd "$PROJECT_DIR"
        eval "$SETUP_CMD"
    else
        echo "No setup command found in SHAKEOUT.md. Skipping."
    fi

    # Extract URL from SHAKEOUT.md
    WEB_URL=$(grep -A1 '^## URL' "$PROJECT_DIR/SHAKEOUT.md" | tail -1 | tr -d '[:space:]' || echo "")
    if [ -z "$WEB_URL" ]; then
        WEB_URL="http://localhost:3000"
    fi

    cat > "$ENVFILE" <<EOF
SHAKEOUT_WEB_URL=$WEB_URL
SHAKEOUT_PROJECT_DIR=$PROJECT_DIR
EOF

    echo "Setup complete. URL: $WEB_URL"
else
    echo "Already set up (run --teardown to reset)."
fi

source "$ENVFILE"
export SHAKEOUT_WEB_URL SHAKEOUT_PROJECT_DIR

if [ "$ACTION" = "setup" ]; then
    exit 0
fi

# ── Create worktree ─────────────────────────────────────────────────────
if [ -z "$WORKTREE_DIR" ]; then
    cd "$PROJECT_DIR"
    git fetch origin 2>/dev/null || true

    BRANCH_NAME="shakeout/$(date +%Y%m%d-%H%M%S)"
    WORKTREE_DIR="$PROJECT_DIR/.worktrees/$BRANCH_NAME"
    mkdir -p "$(dirname "$WORKTREE_DIR")"

    # Use origin/main if available, fall back to main, fall back to HEAD
    BASE_REF=$(git rev-parse --verify origin/main 2>/dev/null \
        || git rev-parse --verify main 2>/dev/null \
        || git rev-parse HEAD)
    git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" "$BASE_REF"
fi

cd "$WORKTREE_DIR"
echo "WORKTREE_DIR=$WORKTREE_DIR" > "$STATEFILE"

echo ""
echo "=== Starting Shakeout: $PROJECT_NAME ==="
echo "Worktree: $WORKTREE_DIR"
echo "Web URL:  $SHAKEOUT_WEB_URL"
echo ""

# ── Launch Claude Code ──────────────────────────────────────────────────
# Combine generic cycle prompt with project-specific SHAKEOUT.md
GENERIC_PROMPT=$(cat "$SCRIPT_DIR/prompt.md")
PROJECT_PROMPT=$(cat "$PROJECT_DIR/SHAKEOUT.md")

FULL_PROMPT="$GENERIC_PROMPT

---

$PROJECT_PROMPT"

if [ -f "$WORKTREE_DIR/.claude/settings.local.json" ]; then
    claude --dangerously-skip-permissions --chrome --continue
else
    claude --dangerously-skip-permissions --chrome "/loop 10m $FULL_PROMPT"
fi
