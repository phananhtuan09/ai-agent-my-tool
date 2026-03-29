# AI Agent Tool

## Overview

AI Agent Tool is a FastAPI application with an HTMX and Jinja2 frontend for running a small set of personal automation agents from one web interface.

The project currently ships with two agent consoles and one shared config page:

- `Config` for managing the shared OpenAI base URL, API key, connectivity test, and model catalog
- `Daily Scheduler` for turning a task list into a working-day schedule
- `Crypto Airdrop` for tracking and filtering ranked airdrop opportunities

The UI is served as server-rendered pages, while live updates are pushed through Server-Sent Events (SSE). Each agent keeps its own local SQLite storage, and runtime behavior is configured through `config/settings.yaml`.

## Features

- Unified dashboard for all registered agents
- Per-agent pages with dedicated controls, results, and live activity
- Hot-swappable model configuration from the UI
- YAML-based runtime settings for schedules, enabled sources, and shared OpenAI config
- SSE-powered status, chat, notification, and UI update streams
- Local per-agent persistence with SQLite
- Dark professional UI with responsive layouts and table-based result views

### Included pages

#### Config

- Manages the shared OpenAI-compatible base URL and API key
- Tests connectivity against the configured endpoint
- Fetches and persists the shared model catalog for agent model pickers

#### Daily Scheduler

- Converts a plain-text task list into a daily timeline
- Supports reminder and reset cron schedules
- Tracks task progress through chat-style updates
- Rebuilds the remaining schedule when priorities change

#### Crypto Airdrop

- Tracks ranked airdrop opportunities from supported sources
- Supports manual runs and scheduled refreshes
- Includes chat-based filtering on the latest results
- Uses fixture data by default, with optional live fetch support

## Local Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

### 3. Configure API keys

Use `config/.env.example` as a reference:

```env
OPENAI_API_KEY=replace-me
```

This project reads the OpenAI API key from process environment variables or the persisted `config/.env` file written by the config page.

Example:

```bash
export OPENAI_API_KEY="your-key"
```

### 4. Review runtime settings

Main runtime configuration lives in `config/settings.yaml`.

This file controls:

- shared OpenAI base URL and model catalog
- per-agent model overrides
- cron schedules
- enabled sources
- daily scheduler runtime options

You can also override the settings file path with:

```bash
export AI_AGENT_TOOL_SETTINGS_PATH="/absolute/path/to/settings.yaml"
```

### 5. Start the application

```bash
uvicorn backend.main:app --reload
```

By default, the app will be available at:

```text
http://127.0.0.1:8000
```

### 6. Optional: enable live airdrop fetching

The crypto airdrop agent uses fixture data by default. To allow live source fetching:

```bash
export AI_AGENT_TOOL_ENABLE_LIVE_AIRDROP_FETCH=1
```

## Useful Routes

- `/` dashboard
- `/config`
- `/agents/daily_scheduler`
- `/agents/crypto_airdrop`
- `/stream/{agent_name}` SSE stream endpoint

## Development Notes

- Backend: FastAPI
- Frontend: Jinja2 templates + HTMX + static JavaScript
- Scheduling: APScheduler
- Storage: per-agent SQLite databases
- Tests: `pytest`

Run tests with:

```bash
pytest
```
