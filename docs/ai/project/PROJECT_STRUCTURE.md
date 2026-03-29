# Project Structure

> This document can be auto-generated via `generate-standards`. Edit manually as needed.

<!-- GENERATED: PROJECT_STRUCTURE:START -->

## Folder Layout

```
ai-agent-tool/
├── backend/                          # Python FastAPI application
│   ├── main.py                       # FastAPI app entry point, lifespan events
│   ├── shared/                       # Shared utilities (never import agents here)
│   │   ├── llm_client.py             # OpenAI runtime descriptor for model + base URL state
│   │   ├── web_search.py             # duckduckgo-search wrapper
│   │   └── crawler.py                # Playwright async crawler
│   ├── agents/                       # One folder per agent (feature-based)
│   │   ├── _registry.py              # Auto-discover + register all agents
│   │   ├── base_agent.py             # Abstract BaseAgent: stream(), run(), tools
│   │   ├── daily_scheduler/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py              # Chat-driven: create/update/reschedule
│   │   │   ├── tools.py              # create_schedule(), reschedule(), render_schedule()
│   │   │   ├── skills.py             # Scheduling + estimation prompt templates
│   │   │   ├── cron.py               # APScheduler: hourly push to SSE chat
│   │   │   └── memory.db             # SQLite: today's tasks only
│   │   └── crypto_airdrop/
│   │       ├── __init__.py
│   │       ├── agent.py              # Cron crawl + chat interface
│   │       ├── tools.py              # fetch_airdrops(), analyze(), render_list()
│   │       ├── skills.py             # Airdrop evaluation criteria prompts
│   │       ├── cron.py               # APScheduler: every 6h crawl
│   │       └── memory.db             # SQLite: airdrops tracked
│   ├── api/                          # FastAPI route handlers
│   │   ├── daily_scheduler.py        # POST /chat, GET /schedule
│   │   ├── crypto_airdrop.py         # POST /chat, GET /airdrops
│   │   ├── config.py                 # GET/POST OpenAI config actions and model override modal
│   │   └── stream.py                 # GET /stream/{agent} — SSE endpoint
│   └── exceptions.py                 # AgentError, ConfigError, CrawlError, LLMError
│
├── frontend/                         # HTMX + Jinja2 templates
│   ├── templates/
│   │   ├── base.html                 # Nav + global SSE listener + Notification API
│   │   ├── dashboard.html            # Active agent cards with status
│   │   ├── config.html               # Dedicated OpenAI config page
│   │   ├── daily_scheduler.html      # Timeline panel | Chat panel
│   │   └── crypto_airdrop.html       # Airdrop cards | Chat panel
│   └── static/
│       ├── app.js                    # SSE router: chat / ui_update / notify events
│       └── style.css
│
├── config/
│   ├── .env                          # OPENAI_API_KEY (never commit)
│   └── settings.yaml                 # Shared OpenAI config plus per-agent runtime settings
│
└── docs/
    └── ai/
        ├── project/                  # This folder: conventions + structure
        ├── planning/                 # Epic + feature planning docs
        └── testing/                  # Test plans (post-MVP)
```

---

## Module Boundaries & Dependency Rules

```
frontend → api → agents → shared
                       ↘ exceptions

agents/*/  → shared/llm_client, shared/web_search, shared/crawler
agents/*/  → agents/base_agent  (inherit only)
agents/*/  NEVER import from other agents/*/
shared/    NEVER import from agents/
api/       imports from agents/ and shared/
```

---

## Design Patterns

| Pattern | Where | Description |
|---------|-------|-------------|
| **Agent Registry** | `agents/_registry.py` | Auto-discovers agents; adding a new tool = new folder + register() |
| **BaseAgent** | `agents/base_agent.py` | Abstract interface: `stream()`, `run()`, tool definitions |
| **Tool Call → UI Update** | All agents | Agent calls `render_*()` tool → SSE `ui_update` event → frontend panel |
| **SSE Fan-out** | `api/stream.py` | One persistent SSE connection per agent; multiplexes chat/ui/notify |
| **Cron → Chat Push** | `*/cron.py` | APScheduler jobs push SSE `notify` events into the chat panel |

---

## Config & Secrets

- **`.env`**: API keys only. Loaded via `python-dotenv`. Never committed to Git.
- **`settings.yaml`**: Per-agent runtime config (model, cron, filter keywords). Hot-reload supported.
- **`memory.db`**: Per-agent SQLite. Auto-created on first run. Stored in `agents/{name}/`.

---

## Test Configuration

> Tests skipped for MVP. Add pytest when needed post-MVP.

### Unit Tests (post-MVP)
- Framework: pytest + pytest-asyncio
- Run command: `pytest tests/unit/`
- Config file: `pytest.ini`
- Test location: `tests/unit/`
- File pattern: `test_*.py`

### Integration Tests (post-MVP)
- Framework: Playwright (Python)
- Run command: `pytest tests/integration/`
- Test location: `tests/integration/`
- File pattern: `test_*.py`

<!-- GENERATED: PROJECT_STRUCTURE:END -->

## AI Agent Workflow Assets
- `.claude/`: single source of truth for workflow content and migration inputs
- `.claude/commands/`: primary workflow commands to author and sync from
- `.claude/skills/`: primary skill definitions to author and sync from
- `.claude/agents/`: primary worker-role prompts to author and sync from
- `.claude/output-styles/`: primary response style definitions to author and sync from
- `.claude/themes/`: primary theme presets to author and sync from
- `.claude/scripts/`: reusable workflow scripts to sync from when needed
- `.agents/skills/`: Codex compatibility copies and native runtime skill mirrors
- `.agents/roles/`: Codex compatibility copies for worker roles
- `.agents/themes/`: Codex compatibility copies for theme assets

## AI Docs Roles (existing only)
- `docs/ai/project/`: repository-wide conventions and structure; workflow overview and navigation live in `README.md`.
- `docs/ai/planning/`: epic tracking docs and feature plans; use `epic-template.md` to decompose large requirements and `feature-template.md` to drive task execution.
- `docs/ai/testing/`: test plans and results
  - `unit-{name}.md`: unit test docs (from `/writing-test`)
  - `integration-{name}.md`: integration test docs (from `/writing-integration-test`)
  - `web-{name}.md`: browser UI test docs (from `/test-web-orchestrator`)
  - Run tests via `/run-test` command
- `docs/ai/tooling/`: cross-tool capability mapping and migration references used by sync workflows

## Guiding Questions (for AI regeneration)
- How is the codebase organized by domain/feature vs layers?
- What are the module boundaries and dependency directions to preserve?
- Which design patterns are officially adopted and where?
- Where do configs/secrets live and how are they injected?
- What is the expected test file placement and naming?
- Any build/deployment constraints affecting structure (monorepo, packages)?
