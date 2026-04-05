#!/bin/bash
# Test: README persona selection claims match command implementations
#
# README says "Every command picks a random persona unless you pass --persona"
# but /interview requires --persona. The README should note this exception.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

# Check if README claims all commands pick random personas
if grep -q "Every command picks a random persona" "$REPO_ROOT/README.md"; then
  echo "README claims: every command picks a random persona"

  # Check if interview command says --persona is required
  if grep -q "required for interview" "$REPO_ROOT/commands/interview.md"; then
    echo "FAIL: interview command requires --persona, contradicting README's 'every command' claim"
    echo "  README should note that /interview requires --persona"
    FAIL=1
  else
    echo "PASS: no contradiction found"
  fi
else
  echo "PASS: README does not make blanket 'every command' claim about persona selection"
fi

exit $FAIL
