#!/usr/bin/env bash
# weekly directory re-verification cron.
#
# runs npm run check:directory (which HEAD-checks every source_url and flags
# entries older than 180 days). on failure or warnings, notifies via TG +
# local notification. clean runs are logged but silent.
#
# wired via Library/LaunchAgents/com.xavier.singaporerabbit.directory-reverify.plist

set -uo pipefail

cd "$(dirname "$0")/.."
LOG=".logs/directory-reverify.log"
mkdir -p .logs

TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "===== $TS =====" >> "$LOG"

OUTPUT=$(/opt/homebrew/bin/npm run check:directory 2>&1)
RC=$?
echo "$OUTPUT" >> "$LOG"
echo "exit code: $RC" >> "$LOG"

# parse the validator's last line: "directory validator: checked N entries, X errors, Y warnings."
SUMMARY=$(echo "$OUTPUT" | grep -E 'directory validator:' | tail -1)
ERRORS=$(echo "$SUMMARY" | grep -oE '[0-9]+ errors?' | head -1 | grep -oE '[0-9]+' || echo "0")
WARNS=$(echo "$SUMMARY" | grep -oE '[0-9]+ warnings?' | head -1 | grep -oE '[0-9]+' || echo "0")

if [ "$RC" -ne 0 ] || [ "$ERRORS" -gt 0 ]; then
  scripts/tg-notify.sh "directory check FAILED ($ERRORS errors, $WARNS warnings). see $LOG" "rabbits reverify"
elif [ "$WARNS" -gt 0 ]; then
  scripts/tg-notify.sh "directory check passed with $WARNS warnings. see $LOG" "rabbits reverify"
fi

exit 0
