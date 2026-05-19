#!/usr/bin/env bash
# forever-loop wrapper around auto_publish.sh.
#
# WHY: launchd-spawned npm fails with EPERM uv_cwd on ~/Desktop without
# Full Disk Access. running this from a user terminal via nohup inherits
# the user's FDA, so npm + rsync work normally.
#
# usage:
#   nohup bash scripts/factory/auto_publish_loop.sh > /tmp/publish-loop.log 2>&1 &
#   disown
#
# stop:
#   pgrep -f auto_publish_loop.sh | xargs kill
set -u
INTERVAL="${INTERVAL:-1800}"  # 30 min default
SCRIPT="/Users/foktunghoe/Desktop/singaporerabbits/scripts/factory/auto_publish.sh"

while true; do
  echo "[$(date -Iseconds)] loop tick"
  bash "$SCRIPT"
  echo "[$(date -Iseconds)] tick exit $?"
  sleep "$INTERVAL"
done
