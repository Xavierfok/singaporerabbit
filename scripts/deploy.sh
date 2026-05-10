#!/usr/bin/env bash
# deploy singaporerabbit.com to .25 (farm4) over SSH.
#
# - builds dist/ locally
# - rsyncs to a timestamped releases/ dir on the server
# - atomic-symlinks current → new release
# - reloads nginx (cheap reload, no downtime)
# - keeps the last 5 releases, prunes older
# - optionally pings IndexNow if INDEXNOW_KEY is set
#
# usage: npm run deploy
set -euo pipefail

SSH_HOST=${SSH_HOST:-farm4}
SITE_ROOT=${SITE_ROOT:-/var/www/singaporerabbits}
KEEP_RELEASES=${KEEP_RELEASES:-5}

cd "$(dirname "$0")/.."

RELEASE=$(date +%Y%m%d-%H%M%S)
echo "==> deploying release $RELEASE to $SSH_HOST:$SITE_ROOT"

echo "==> 1/5 build"
npm run build >/dev/null

if [ ! -d dist ] || [ -z "$(ls -A dist 2>/dev/null)" ]; then
  echo "build produced no dist/, aborting" >&2
  exit 1
fi

echo "==> 2/5 rsync to $SSH_HOST"
ssh "$SSH_HOST" "mkdir -p $SITE_ROOT/releases/$RELEASE/dist"
rsync -az --delete dist/ "$SSH_HOST:$SITE_ROOT/releases/$RELEASE/dist/"

echo "==> 3/5 flip symlink + reload nginx"
ssh "$SSH_HOST" "
  set -e
  cd $SITE_ROOT
  ln -sfn releases/$RELEASE current.new
  mv -Tf current.new current
  sudo nginx -t >/dev/null
  sudo systemctl reload nginx
"

echo "==> 4/5 prune old releases (keep $KEEP_RELEASES)"
ssh "$SSH_HOST" "
  cd $SITE_ROOT/releases
  ls -1t | tail -n +\$(($KEEP_RELEASES + 1)) | xargs -r rm -rf
  ls -1t
"

echo "==> 5/5 smoke test origin"
SAMPLED_HASH=$(ssh "$SSH_HOST" "curl -s -H 'Host: singaporerabbit.com' http://127.0.0.1:8081/ | md5sum | cut -d' ' -f1")
LOCAL_HASH=$(md5sum dist/index.html | cut -d' ' -f1)
if [ "$SAMPLED_HASH" != "$LOCAL_HASH" ]; then
  echo "ERROR: origin nginx serving wrong bytes. expected $LOCAL_HASH, got $SAMPLED_HASH" >&2
  exit 1
fi
echo "    origin checksum match: $LOCAL_HASH"

if [ -n "${INDEXNOW_KEY:-}" ]; then
  echo "==> bonus: indexnow ping"
  npm run indexnow || echo "    indexnow ping failed (non-fatal)"
else
  echo "    INDEXNOW_KEY not set, skipping indexnow ping"
fi

echo "==> deploy complete: $RELEASE"
