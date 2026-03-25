#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
ENV_FILE="$ROOT_DIR/config/.env"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but was not found in PATH." >&2
  exit 1
fi

create_venv() {
  echo "Creating virtual environment at .venv"
  python3 -m venv "$VENV_DIR"
}

create_venv_with_virtualenv() {
  echo "Falling back to virtualenv"
  python3 -m pip install --user --break-system-packages virtualenv
  python3 -m virtualenv "$VENV_DIR"
}

if [ ! -x "$VENV_PYTHON" ]; then
  create_venv || true
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "Detected incomplete virtual environment. Rebuilding .venv"
  rm -rf "$VENV_DIR"
  create_venv || true
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  rm -rf "$VENV_DIR"
  create_venv_with_virtualenv
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "Error: failed to prepare a working virtual environment with pip." >&2
  exit 1
fi

if ! "$VENV_PYTHON" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "Installing project dependencies"
  "$VENV_PYTHON" -m pip install -e ".[dev]"
fi

if [ -f "$ENV_FILE" ]; then
  echo "Loading environment from config/.env"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [ -z "${AI_AGENT_TOOL_SETTINGS_PATH:-}" ]; then
  export AI_AGENT_TOOL_SETTINGS_PATH="$ROOT_DIR/config/settings.yaml"
fi

echo "Starting AI Agent Tool on http://$HOST:$PORT"
exec "$VENV_PYTHON" -m uvicorn backend.main:app --reload --host "$HOST" --port "$PORT"
