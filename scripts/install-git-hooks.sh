#!/usr/bin/env bash
# install singaporerabbit git pre-commit hooks. run once per clone:
#   bash scripts/install-git-hooks.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_DST="$REPO_ROOT/.git/hooks/pre-commit"
HOOK_SRC="$REPO_ROOT/scripts/git-hooks/pre-commit"

if [ ! -f "$HOOK_SRC" ]; then
  echo "ERROR: $HOOK_SRC not found" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/.git/hooks"
cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "installed pre-commit hook -> $HOOK_DST"
