#!/usr/bin/env bash
#
# Local deploy for hired.uz — does exactly what .github/workflows/deploy.yml does,
# but from your machine (no GitHub Actions / billing needed).
#
# Usage:  ./deploy.sh
# Uses your SSH host alias "myserver" by default; override with DEPLOY_HOST=...
#
set -euo pipefail

HOST="${DEPLOY_HOST:-myserver}"
cd "$(dirname "$0")"

echo "==> Building dashboard"
( cd dashboard && npm ci && npm run build )

echo "==> Syncing dashboard -> /var/www/gethired"
rsync -az --delete dashboard/dist/ "$HOST:/var/www/gethired/"

echo "==> Syncing backend -> ~/gethired"
rsync -az --delete \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='dashboard' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='data' \
  --exclude='chroma_db' \
  --exclude='bot.lock' \
  ./ "$HOST:gethired/"

echo "==> Installing deps & restarting services"
ssh "$HOST" 'cd ~/gethired \
  && ./venv/bin/pip install -r requirements.txt --quiet \
  && sudo systemctl restart gethired-api \
  && sudo systemctl restart gethired-bot \
  && sleep 4 \
  && systemctl is-active gethired-api gethired-bot'

echo "✅ Deployed to https://gethired.muzaffar.zip"
