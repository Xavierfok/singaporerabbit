#!/usr/bin/env bash
# rabbits content factory daily runner.
# wired via Library/LaunchAgents/com.xavier.singaporerabbit.factory.plist
# (daily 10am SGT)
set -u
export PATH="/opt/homebrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset ANTHROPIC_API_KEY
unset CLAUDE_API_KEY

ROOT="/Users/foktunghoe/Desktop/singaporerabbits/scripts/factory"
LOG="$ROOT/logs/cron.log"
mkdir -p "$ROOT/logs"

echo "===== $(date -Iseconds) =====" >> "$LOG"
cd /Users/foktunghoe/Desktop/singaporerabbits || exit 1

# ensure main is up to date before factory branches off
git fetch origin >> "$LOG" 2>&1
git checkout main >> "$LOG" 2>&1
git pull --ff-only origin main >> "$LOG" 2>&1

/opt/homebrew/bin/python3 "$ROOT/generate.py" "$@" >> "$LOG" 2>&1
RC=$?
echo "exit $RC" >> "$LOG"
exit $RC
