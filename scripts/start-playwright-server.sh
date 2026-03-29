#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="${PLAYWRIGHT_TMP_DIR:-$ROOT_DIR/.playwright}"
SETTINGS_TEMPLATE="$ROOT_DIR/config/settings.yaml"
ENV_TEMPLATE="$ROOT_DIR/config/.env"
TMP_SETTINGS="$TMP_DIR/settings.yaml"
TMP_ENV="$TMP_DIR/.env"
PYTHON_BIN="${PLAYWRIGHT_PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

mkdir -p "$TMP_DIR"
cp "$SETTINGS_TEMPLATE" "$TMP_SETTINGS"
if [ -f "$ENV_TEMPLATE" ]; then
  cp "$ENV_TEMPLATE" "$TMP_ENV"
else
  : > "$TMP_ENV"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    echo "Error: no Python interpreter available for Playwright webServer." >&2
    exit 1
  fi
fi

export AI_AGENT_TOOL_SETTINGS_PATH="$TMP_SETTINGS"
export AI_AGENT_TOOL_ENV_PATH="$TMP_ENV"

exec "$PYTHON_BIN" -m uvicorn backend.main:app --host "$HOST" --port "$PORT"
