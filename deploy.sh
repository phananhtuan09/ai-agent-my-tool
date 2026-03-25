#!/usr/bin/env bash
# Deploy script for VPS updates
# Flow:
# 1. Ensure the git worktree is clean
# 2. Pull the latest code from origin/main
# 3. Sync Python dependencies inside .venv
# 4. Restart the PM2 app with production env

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
APP_NAME="${APP_NAME:-ai-agent-tool}"

cd "$ROOT_DIR"

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v pm2 >/dev/null 2>&1; then
  echo "Error: pm2 is required but was not found in PATH." >&2
  exit 1
fi

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: .venv is missing. Run ./run-local.sh or complete first-time setup first." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: this directory is not a git repository." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: git worktree is not clean. Commit or stash local changes before deploy." >&2
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  echo "Switching branch from $CURRENT_BRANCH to $BRANCH"
  git checkout "$BRANCH"
fi

echo "Fetching latest code from $REMOTE/$BRANCH"
git fetch "$REMOTE" "$BRANCH"
git pull --ff-only "$REMOTE" "$BRANCH"

echo "Installing/updating Python dependencies"
"$VENV_PYTHON" -m pip install -e .

echo "Restarting PM2 app: $APP_NAME"
pm2 startOrRestart ecosystem.config.cjs --only "$APP_NAME" --env production
pm2 save

echo "Deploy complete."
echo "App status:"
pm2 status "$APP_NAME"
