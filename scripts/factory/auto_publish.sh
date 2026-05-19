#!/usr/bin/env bash
# auto-publish watcher: push + deploy whenever HEAD differs from last deploy.
# safe to run alongside the drain — git push is atomic and deploy uses
# working-tree-only state (no rebase, no merge).
#
# wired via Library/LaunchAgents/com.xavier.singaporerabbit.publish.plist
# every 30 minutes.
set -u
export PATH="/opt/homebrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset ANTHROPIC_API_KEY
unset CLAUDE_API_KEY

REPO="/Users/foktunghoe/Desktop/singaporerabbits"
LAST_SHA="$REPO/scripts/factory/.last-deployed-sha"
LOG="$REPO/scripts/factory/logs/auto_publish.log"
LOCK="$REPO/scripts/factory/auto_publish.lock"
mkdir -p "$REPO/scripts/factory/logs"

cd "$REPO" || exit 1

# single-instance lock
if [ -f "$LOCK" ]; then
  OLD_PID=$(cat "$LOCK" 2>/dev/null || echo "")
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "$(date -Iseconds) another auto_publish running (pid $OLD_PID), skip" >> "$LOG"
    exit 0
  fi
  rm -f "$LOCK"
fi
echo "$$" > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

# what's the current HEAD?
CURRENT=$(git rev-parse HEAD 2>/dev/null || echo "")
if [ -z "$CURRENT" ]; then
  echo "$(date -Iseconds) git rev-parse failed, skip" >> "$LOG"
  exit 1
fi

# compare to last deployed
PREV=""
[ -f "$LAST_SHA" ] && PREV=$(cat "$LAST_SHA")
if [ "$CURRENT" = "$PREV" ]; then
  echo "$(date -Iseconds) HEAD unchanged ($CURRENT), skip" >> "$LOG"
  exit 0
fi

echo "$(date -Iseconds) HEAD changed: $PREV -> $CURRENT, publishing..." >> "$LOG"

# push to origin (if local has unpushed commits)
git push origin main >> "$LOG" 2>&1
PUSH_RC=$?
echo "push rc=$PUSH_RC" >> "$LOG"

# deploy: build + rsync + nginx reload + indexnow
/opt/homebrew/bin/npm run deploy >> "$LOG" 2>&1
DEPLOY_RC=$?
echo "deploy rc=$DEPLOY_RC" >> "$LOG"

# mark deployed only if deploy succeeded
if [ "$DEPLOY_RC" = "0" ]; then
  echo "$CURRENT" > "$LAST_SHA"
  echo "$(date -Iseconds) published $CURRENT" >> "$LOG"
fi

exit $DEPLOY_RC
