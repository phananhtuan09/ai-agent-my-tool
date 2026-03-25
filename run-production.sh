#!/usr/bin/env bash
# Production startup script for ai-agent-tool
# Usage: ./run-production.sh
# This script is for manual first-time startup or debugging.
# Normal operation: pm2 start ecosystem.config.cjs --env production

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
ENV_FILE="$ROOT_DIR/config/.env"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8008}"

cd "$ROOT_DIR"

# Ensure venv exists
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: .venv not found. Run: python3 -m venv .venv && .venv/bin/pip install -e ." >&2
  exit 1
fi

# Load .env if present
if [ -f "$ENV_FILE" ]; then
  echo "Loading environment from config/.env"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

export AI_AGENT_TOOL_SETTINGS_PATH="${AI_AGENT_TOOL_SETTINGS_PATH:-$ROOT_DIR/config/settings.yaml}"

echo "Starting AI Agent Tool (production) on ${HOST}:${PORT}"
exec "$VENV_PYTHON" -m uvicorn backend.main:app \
  --host "$HOST" \
  --port "$PORT"
