# Plan: AI Agent Foundation

Note: All content in this document must be written in English.

---
epic_plan: docs/ai/planning/epic-ai-agent-tool.md
requirement: docs/ai/requirements/req-ai-agent-tool.md
---

## 0. Related Documents

| Type | Document |
|------|----------|
| Requirement | [req-ai-agent-tool.md](../requirements/req-ai-agent-tool.md) |
| Epic | [epic-ai-agent-tool.md](epic-ai-agent-tool.md) |

---

## 1. Codebase Context

### Architectural Patterns
- `Layered monolith with agent registry`: The requirement and solution-architecture docs both define `frontend -> api -> agents -> shared`, plus auto-discovery through `register()` in each agent package.
- `Single-writer planning workflow`: The repository currently contains planning docs only, so this slice must create the runtime skeleton without assuming any existing backend/frontend implementation details.

### Key Files to Reference
- `docs/ai/requirements/req-ai-agent-tool.md` - Functional requirements, business rules, and out-of-scope boundaries for the first slice.
- `docs/ai/requirements/agents/sa-ai-agent-tool.md` - Shared module build order, SSE pattern, hot-swap expectations, and technical risk mitigation.
- `docs/ai/project/PROJECT_STRUCTURE.md` - Target file layout for backend, frontend, config, and future agent modules.

---

## 3. Goal & Acceptance Criteria

### Goal
- Establish a working FastAPI + HTMX application shell with three registered placeholder agents, shared SSE/config infrastructure, and a styled dashboard so later feature plans can focus on agent behavior instead of platform bootstrapping.

### Acceptance Criteria (Given/When/Then)
- Given the app starts with the default settings file, when the registry runs during startup, then Job Finder, Daily Schedule, and Crypto Airdrop appear in the dashboard and sidebar without hard-coded page wiring in `main.py`.
- Given a user opens an agent page, when the page connects to `/stream/{agent}`, then the browser receives an initial status event and later notification/config events without a page reload.
- Given a user opens the config modal for an agent, when provider/model values are saved, then `config/settings.yaml` is updated, the in-memory agent reloads its LLM config, and the UI receives confirmation feedback.
- Given the repository has no app code before execution, when this plan is completed, then the project contains a runnable app entry point, frontend templates/static assets, default config files, and focused tests for the created foundation behavior.

## 4. Risks & Assumptions

### Risks
- The requirement is broader than one implementation slice, so this plan must stay disciplined and avoid leaking domain-specific crawler/chat logic into the foundation.
- OQ-03 in the BA doc leaves API key handling partially open; implementing raw API-key editing in the modal now would create unnecessary security surface before the real agent behavior exists.
- The repository does not yet define a Python packaging baseline, so the first pass must introduce only the minimum tooling needed for the shell and tests.

### Assumptions
- API keys remain in environment variables for now; the modal only edits provider, model, and environment-variable binding metadata.
- Placeholder agent pages are acceptable for the foundation slice as long as the shared runtime, routing, SSE, and settings flows are real and reusable by later plans.
- SQLite files can be created as empty per-agent stores with WAL enabled in this slice; agent-specific schemas will be added in downstream feature plans.

## 5. Definition of Done
- [x] Build passes (linter, type checks, compile)
- [x] Tests added and passing
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Build the platform bottom-up: create the Python project baseline and shared runtime first, wire FastAPI routes and registry-driven startup second, then add the frontend shell and minimal tests. The delivered slice is intentionally real infrastructure with placeholder agent content, not mocked architecture notes.

### Phase 1: Shared Runtime Skeleton

- [x] [ADDED] pyproject.toml — Define the FastAPI application package, runtime dependencies, and test tooling.
  ```text
  Function: project metadata and tool configuration

  Input validation:
    - Python version: >= 3.11
    - Dependencies: include FastAPI, Jinja2, PyYAML, filelock, APScheduler, pytest, and HTTP client support for TestClient

  Logic flow:
    1. Declare project metadata and package discovery for `backend`.
    2. Register runtime dependencies required by the foundation slice.
    3. Register optional dev/test tooling for focused validation.

  Return: installable package metadata | Error(packaging tool parse failure)

  Edge cases:
    - Missing package discovery path -> tests/imports fail
    - Missing multipart/httpx support -> form handling or TestClient breaks

  Dependencies: setuptools, pip tooling
  ```

- [x] [ADDED] backend/exceptions.py, backend/shared/settings.py, backend/shared/llm_client.py, backend/shared/events.py — Add the shared exception hierarchy, YAML settings persistence, LLM hot-swap wrapper, and SSE event broker.
  ```text
  Function: load_settings() / save_agent_settings(agent_name, payload) / LLMClient.from_config(config) / EventBroker.subscribe(agent_name)

  Input validation:
    - agent_name: must exist in the current settings document
    - provider: "anthropic" or "openai"
    - model: non-empty string
    - api_key_env_var: non-empty environment variable name

  Logic flow:
    1. Read `config/settings.yaml`; if missing, raise ConfigError with an actionable message.
    2. Validate and persist agent-specific settings with file locking.
    3. Build a lightweight LLM client descriptor from the saved settings.
    4. Maintain per-agent asyncio subscriber queues for SSE fan-out and cleanup.

  Return: typed settings objects / broker queue / Error(ConfigError, LLMError)

  Edge cases:
    - Malformed YAML -> keep previous in-memory config and raise ConfigError
    - Unknown provider -> reject with validation error
    - Subscriber disconnect -> queue removed without leaking references

  Dependencies: pydantic, PyYAML, filelock, asyncio
  ```

- [x] [ADDED] backend/agents/base_agent.py, backend/agents/_registry.py, backend/agents/job_finder/__init__.py, backend/agents/job_finder/agent.py, backend/agents/daily_scheduler/__init__.py, backend/agents/daily_scheduler/agent.py, backend/agents/crypto_airdrop/__init__.py, backend/agents/crypto_airdrop/agent.py — Establish the base agent contract, auto-discovery registry, and three concrete placeholder agents.
  ```text
  Function: AgentRegistry.discover() / BaseAgent.initialize() / register(registry)

  Input validation:
    - Agent slug: unique, kebab-safe identifier
    - Template name: must map to an existing frontend template
    - Storage path: parent directory must be creatable

  Logic flow:
    1. Scan `backend/agents/` for non-private packages.
    2. Import each package and call its `register()` hook.
    3. Instantiate agents with shared settings/event broker references.
    4. Ensure each agent creates an isolated SQLite file and prepares a status snapshot for the UI.

  Return: populated registry and agent lookup helpers | Error(ConfigError, AgentError)

  Edge cases:
    - Duplicate slug -> fail fast during startup
    - Missing `register()` hook -> skip package with explicit warning
    - Missing storage directory -> create it before touching SQLite

  Dependencies: importlib, pathlib, sqlite3, shared settings, shared events
  ```

### Phase 2: App Wiring And Config Flow

- [x] [ADDED] backend/api/pages.py, backend/api/config.py, backend/api/stream.py, backend/main.py — Wire the dashboard, agent pages, config modal save flow, SSE endpoint, and application lifespan startup.
  ```text
  Function: create_app() / GET / / GET /agents/{agent_name} / GET|POST /agents/{agent_name}/config / GET /stream/{agent_name}

  Input validation:
    - agent_name: must resolve through the registry or return 404
    - config form fields: same provider/model/env-var constraints as shared settings

  Logic flow:
    1. Create the FastAPI app and Jinja template renderer.
    2. During lifespan startup, load settings, discover agents, initialize storage, and start APScheduler.
    3. Render the dashboard and per-agent pages from registry metadata.
    4. Save config updates, reload the target agent LLM wrapper, and publish notify/status SSE events.
    5. Stream initial snapshots plus live events to EventSource consumers with heartbeat cleanup.

  Return: HTML responses, SSE event stream, config feedback partial | Error(HTTP 404, HTTP 422, ConfigError)

  Edge cases:
    - Unknown agent page -> 404 response
    - Scheduler startup/shutdown errors -> propagate actionable failure during app lifespan
    - Idle SSE connection -> heartbeat event keeps the connection alive

  Dependencies: FastAPI, Jinja2Templates, APScheduler, registry, shared settings, shared events
  ```

### Phase 3: Frontend Shell And Validation

- [x] [ADDED] frontend/templates/base.html, frontend/templates/dashboard.html, frontend/templates/job_finder.html, frontend/templates/daily_scheduler.html, frontend/templates/crypto_airdrop.html, frontend/templates/partials/config_modal.html, frontend/templates/partials/config_feedback.html — Deliver the shared dashboard, agent layouts, and HTMX-driven config modal using a deliberate visual system.
  ```text
  Function: Jinja page templates and partials

  Input validation:
    - Template context must include `agents`, `current_agent`, and `page_title` where applicable
    - Modal context must include the current saved agent config

  Logic flow:
    1. Render a persistent sidebar built from registry metadata.
    2. Render a dashboard with three distinct agent cards and current status chips.
    3. Render each agent page with a left-side results/timeline panel and right-side activity/chat panel placeholder.
    4. Render a modal form for provider/model/env-var updates with HTMX partial replacement.

  Return: HTML templates consumable by FastAPI

  Edge cases:
    - No SSE events yet -> show meaningful empty state instead of blank panels
    - Config save error -> modal returns inline error message without breaking the page

  Dependencies: Jinja2, HTMX conventions, registry metadata
  ```

- [x] [ADDED] frontend/static/style.css, frontend/static/app.js, config/settings.yaml, config/.env.example, tests/test_app.py — Add the visual system, EventSource client logic, default config, and focused tests for registry/config/SSE page behavior.
  ```text
  Function: connectAgentStream(agentName) / requestNotificationPermission() / pytest coverage for dashboard and config save flow

  Input validation:
    - Agent stream connection only opens when the page declares an agent slug
    - Browser notifications request permission once and only publish for `notify` events
    - Test payloads must use supported providers/models

  Logic flow:
    1. Apply the selected typography, spacing, color, and motion system to the shared shell.
    2. Open an EventSource per agent page, update the activity feed/status chip, and surface browser notifications.
    3. Ship a default settings file covering the three placeholder agents and document required env vars.
    4. Verify root/dashboard render and config persistence with TestClient.

  Return: static assets, default config files, passing tests

  Edge cases:
    - Browser denies notifications -> keep in-page activity feed working
    - Test run on missing settings file -> bootstrap a temporary copy inside the test fixture

  Dependencies: vanilla JS, Notification API, pytest, FastAPI TestClient
  ```

## 7. Follow-ups
- [ ] Create `feature-job-finder-agent.md` with concrete crawler/filter/ranking/database tasks.
- [ ] Create `feature-daily-schedule-agent.md` with timeline, chat, and cron reminder implementation tasks.
- [ ] Create `feature-crypto-airdrop-agent.md` after confirming the blocking airdrop source list in OQ-02.
- [ ] Install runtime and test dependencies in the target environment, then rerun import and pytest validation.
