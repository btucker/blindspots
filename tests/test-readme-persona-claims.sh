#!/bin/bash
# Test: README persona selection claims match command implementations
#
# /dogfood, /user-trial, /experiment should support random persona selection.
# /interview should present a list for interactive selection.
# README should accurately describe both behaviors.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

# Check that README does NOT make a blanket "every command" claim
if grep -q "Every command picks a random persona" "$REPO_ROOT/README.md"; then
  echo "FAIL: README still makes blanket 'every command' claim about random persona selection"
  FAIL=1
else
  echo "PASS: README does not make blanket persona claim"
fi

# Check that interview command does NOT require --persona
if grep -q "required for interview" "$REPO_ROOT/commands/interview.md"; then
  echo "FAIL: interview command still requires --persona instead of interactive selection"
  FAIL=1
else
  echo "PASS: interview command does not require --persona"
fi

# Check that interview command supports interactive persona selection
if grep -q "present the available personas" "$REPO_ROOT/commands/interview.md" || \
   grep -q "ask the user to pick" "$REPO_ROOT/commands/interview.md"; then
  echo "PASS: interview command supports interactive persona selection"
else
  echo "FAIL: interview command does not describe interactive persona selection"
  FAIL=1
fi

exit $FAIL
