#!/usr/bin/env bash
# sync_tutor.sh
#
# Fast-forwards the tutor worktree's `tutor` branch onto the content
# creator's `main`, so lesson and prompt updates committed on main reach the
# tutor session. Only needed for the worktree fallback (sessions started
# directly in the Claude desktop app, where there's no per-session agent
# picker) -- see scratch-tutor-lesson-runs.md, "Launching the tutor".
#
# Usage: tools/sync_tutor.sh [path-to-worktree]
# Defaults to ../<repo-name>-tutor next to this checkout.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"
WORKTREE_DIR="${1:-$REPO_ROOT/../${REPO_NAME}-tutor}"

if [ ! -e "$WORKTREE_DIR/.git" ]; then
  echo "error: no worktree found at $WORKTREE_DIR" >&2
  echo "create it first: git worktree add $WORKTREE_DIR -b tutor" >&2
  exit 1
fi

echo "syncing $WORKTREE_DIR onto main..."

if ! git -C "$WORKTREE_DIR" merge main --ff-only 2>/tmp/sync_tutor_err.$$; then
  if grep -qi "not possible to fast-forward" /tmp/sync_tutor_err.$$; then
    echo "error: cannot fast-forward -- the tutor branch has commits main doesn't." >&2
    echo "This script never merges non-fast-forward changes automatically." >&2
    echo "Resolve by hand in $WORKTREE_DIR, e.g.:" >&2
    echo "  cd $WORKTREE_DIR && git merge main   # then resolve conflicts yourself" >&2
    rm -f /tmp/sync_tutor_err.$$
    exit 1
  else
    cat /tmp/sync_tutor_err.$$ >&2
    rm -f /tmp/sync_tutor_err.$$
    exit 1
  fi
fi
rm -f /tmp/sync_tutor_err.$$

echo "done: $(git -C "$WORKTREE_DIR" rev-parse --short HEAD)"
