#!/usr/bin/env bash
# rabbits content factory daily runner.
# wired via Library/LaunchAgents/com.xavier.singaporerabbit.factory.plist
# (daily 10am SGT)
#
# bulk mode: COUNT env var sets articles per run (default 50 for 2026-05-18 ramp)
# stops once daily target reached; deploys after batch
set -u
export PATH="/opt/homebrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset ANTHROPIC_API_KEY
unset CLAUDE_API_KEY

ROOT="/Users/foktunghoe/Desktop/singaporerabbits/scripts/factory"
REPO="/Users/foktunghoe/Desktop/singaporerabbits"
LOG="$ROOT/logs/cron.log"
mkdir -p "$ROOT/logs"

COUNT="${COUNT:-50}"

echo "===== $(date -Iseconds) (count=$COUNT) =====" >> "$LOG"
cd "$REPO" || exit 1

# ensure main is up to date before factory commits
git fetch origin >> "$LOG" 2>&1
git checkout main >> "$LOG" 2>&1
git pull --ff-only origin main >> "$LOG" 2>&1

# bulk generation
/opt/homebrew/bin/python3 "$ROOT/generate.py" --count "$COUNT" "$@" >> "$LOG" 2>&1
RC=$?
echo "generate exit $RC" >> "$LOG"

# sweep orphans (mdx files in working tree without queue.json entries)
echo "--- orphan sweep ---" >> "$LOG"
/opt/homebrew/bin/python3 "$ROOT/orphan_sweep.py" >> "$LOG" 2>&1
SWEEP_RC=$?
echo "orphan_sweep exit $SWEEP_RC" >> "$LOG"

# internal-link pass: audit + auto-inject /vets/ link
echo "--- internal-link pass ---" >> "$LOG"
if [ -f "$REPO/scripts/backfill-vets-link.py" ]; then
  /opt/homebrew/bin/python3 "$REPO/scripts/backfill-vets-link.py" --apply >> "$LOG" 2>&1
fi

# commit any auto-fixes from the link pass
cd "$REPO" || exit 1
if ! git diff --quiet HEAD --; then
  git add -A src/content/guides/ >> "$LOG" 2>&1
  git commit -m "factory: internal-link pass after bulk batch

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>" >> "$LOG" 2>&1
  git push origin main >> "$LOG" 2>&1
  echo "link-pass commit pushed" >> "$LOG"
fi

# deploy: build + rsync to farm4 + nginx reload + indexnow ping
echo "--- deploy ---" >> "$LOG"
cd "$REPO" || exit 1
/opt/homebrew/bin/npm run deploy >> "$LOG" 2>&1
DEPLOY_RC=$?
echo "deploy exit $DEPLOY_RC" >> "$LOG"

echo "===== batch complete rc=$RC deploy=$DEPLOY_RC =====" >> "$LOG"
exit $RC
