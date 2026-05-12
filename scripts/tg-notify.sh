#!/usr/bin/env bash
# unified notifier for cron jobs.
#
# usage: scripts/tg-notify.sh "message body" ["title"]
#
# behaviour:
# - if ~/.config/singaporerabbits-tg.env exists with TG_TOKEN + TG_CHAT_ID,
#   sends via @Lifehubxavierbot (or whichever bot the token belongs to)
# - else logs to .logs/notifications.log and shows a macOS notification
#
# to wire TG: create ~/.config/singaporerabbits-tg.env with:
#   TG_TOKEN=<bot-token>
#   TG_CHAT_ID=<your-chat-id>
# you can reuse the Lifehub admin bot token from .46:/home/xavierfok/proxysmart-controller/.env

set -euo pipefail

MSG="${1:-no message}"
TITLE="${2:-singaporerabbit}"
CFG="$HOME/.config/singaporerabbits-tg.env"
LOG="$(cd "$(dirname "$0")/.." && pwd)/.logs/notifications.log"
mkdir -p "$(dirname "$LOG")"

ts() { date '+%Y-%m-%d %H:%M:%S'; }
echo "$(ts) [$TITLE] $MSG" >> "$LOG"

if [ -r "$CFG" ]; then
  set -a
  source "$CFG"
  set +a
  if [ -n "${TG_TOKEN:-}" ] && [ -n "${TG_CHAT_ID:-}" ]; then
    curl -fsS -X POST \
      "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
      -d "chat_id=${TG_CHAT_ID}" \
      -d "text=[${TITLE}] ${MSG}" \
      --max-time 8 >/dev/null 2>&1 || true
  fi
fi

if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"${MSG//\"/\\\"}\" with title \"${TITLE//\"/\\\"}\"" 2>/dev/null || true
fi

exit 0
