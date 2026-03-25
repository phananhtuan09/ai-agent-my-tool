# AI Agent Tool

## Overview

AI Agent Tool is a FastAPI application with an HTMX and Jinja2 frontend for running a small set of personal automation agents from one web interface.

The project currently ships with three agent consoles:

- `Job Finder` for crawling and ranking job listings
- `Daily Scheduler` for turning a task list into a working-day schedule
- `Crypto Airdrop` for tracking and filtering ranked airdrop opportunities

The UI is served as server-rendered pages, while live updates are pushed through Server-Sent Events (SSE). Each agent keeps its own local SQLite storage, and runtime behavior is configured through `config/settings.yaml`.

## Features

- Unified dashboard for all registered agents
- Per-agent pages with dedicated controls, results, and live activity
- Hot-swappable model configuration from the UI
- YAML-based runtime settings for schedules, filters, and enabled sources
- SSE-powered status, chat, notification, and UI update streams
- Local per-agent persistence with SQLite
- Dark professional UI with responsive layouts and table-based result views

### Included agents

#### Job Finder

- Runs manual or scheduled crawls
- Applies hard filters such as salary, location, and framework requirements
- Ranks matched jobs and keeps the latest results in local storage
- Supports source-level enable/disable controls

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
ANTHROPIC_API_KEY=replace-me
OPENAI_API_KEY=replace-me
```

This project reads API keys from process environment variables. It does not auto-load `.env`, so export them in your shell before starting the app.

Example:

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### 4. Review runtime settings

Main runtime configuration lives in `config/settings.yaml`.

This file controls:

- model/provider per agent
- cron schedules
- enabled sources
- filter settings
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
- `/agents/job_finder`
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
