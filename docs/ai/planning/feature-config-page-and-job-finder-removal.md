# Plan: Config Page And Job Finder Removal

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

## 1. Codebase Context

### Similar Features
- `docs/ai/planning/feature-openai-global-config.md` - Existing OpenAI config split that should be extended from modal-only flows to a dedicated page plus live model discovery.
- `backend/api/config.py` - Current HTMX config endpoints already persist OpenAI settings and agent model overrides.

### Reusable Components/Utils
- `backend/shared/settings.py` - Central settings persistence, env handling, and validation helpers for OpenAI settings and per-agent overrides.
- `frontend/templates/partials/config_feedback.html` - Shared inline success/error feedback partial for HTMX config actions.

### Architectural Patterns
- `Registry-backed runtime shell`: active agents come from `AgentRegistry.discover()` and power sidebar, pages, and SSE state.
- `HTMX partial refresh`: config actions return focused partials instead of full-page redirects.

### Key Files to Reference
- `backend/main.py` - Router registration that must stop exposing `job_finder`.
- `backend/agents/_registry.py` - Discovery contract that must align with the reduced active agent list.
- `frontend/templates/base.html` - Shared navigation and action surface for the new dedicated config page.

## 3. Goal & Acceptance Criteria

### Goal
- Replace the modal-only global OpenAI config flow with a dedicated config page that can test the configured API and fetch model names dynamically, while removing the Job Finder experience from the active application.

### Acceptance Criteria (Given/When/Then)
- Given a user opens the config page, when the page renders, then it shows editable `base_url`, API key input, a test/fetch action, and a default-model selector populated from the fetched model list when available.
- Given a user changes `base_url` or API key on the config page, when they trigger the test action, then the app validates the connection against the configured OpenAI-compatible endpoint and returns fetch feedback plus model options without persisting invalid data.
- Given a user saves the config page, when the payload is valid, then `config/settings.yaml` persists the base URL and selected default model, `.env` persists the API key when provided, and active agents hot-swap to the latest global config.
- Given a user opens a non-config screen, when they need to change the model, then they only see the per-agent `Change model` action and the options come from the fetched OpenAI model list rather than a hard-coded tuple.
- Given the app boots or renders navigation after this slice, when active agents are listed, then `job_finder` no longer appears in the sidebar, dashboard, routes, or focused tests.

## 4. Risks & Assumptions

### Risks
- The OpenAI-compatible `GET /models` response can fail because of bad credentials, incompatible proxy behavior, or temporary network issues, so the UI needs a clear fallback state.
- Removing `job_finder` from the active runtime touches routing, tests, settings defaults, and docs; leaving one reference behind would cause broken pages or failing initialization.

### Assumptions
- `Test API` means a live request against the configured OpenAI-compatible models endpoint and not a dry validation-only save.
- `job_finder` should be removed from the active application runtime, not merely hidden from one page.
- Dynamic model validation should stop depending on the previous hard-coded supported-model tuple.

## 5. Definition of Done
- [x] `pytest tests/test_app.py` passes
- [x] `python3 -m compileall backend tests` passes
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Create a dedicated OpenAI config page with HTMX-driven connection testing and model discovery, reuse the discovered model list in agent model modals, and remove the Job Finder agent from the active app wiring, fixtures, and tests.

### Phase 1: Dynamic OpenAI Config Flow

- [x] [MODIFIED] `backend/shared/settings.py`, `backend/api/config.py`, `backend/shared/openai_catalog.py`, `backend/shared/llm_client.py` - Remove hard-coded model validation, add dynamic model fetching helpers, and support HTMX test/fetch responses for the config page.
  ```text
  Endpoint: GET /config | POST /config/openai | POST /config/openai/test

  Input validation:
    - base_url: required trimmed URL-like string
    - api_key: optional on save, required for live test when no stored key exists
    - default_model: required non-empty string on save

  Logic flow:
    1. Normalize and persist OpenAI settings without using a static supported-model tuple.
    2. Call the configured OpenAI-compatible models endpoint to validate connectivity and collect model IDs.
    3. Reuse fetched model IDs for both the config page and per-agent model modal rendering.
    4. Keep save and test actions separate so invalid connection checks do not overwrite persisted settings.

  Return: HTML page/partials | Error(400, message) | Error(422, message)

  Edge cases:
    - Missing API key -> show actionable inline error
    - Endpoint responds without model data -> show error and keep current selection visible
    - Current selected model not in fetched list -> retain it as a fallback option so the form stays editable

  Dependencies: `httpx`, settings helpers, registry hot-swap
  ```

### Phase 2: Page And Modal UX Update

- [x] [MODIFIED] `frontend/templates/base.html`, `frontend/templates/dashboard.html`, `frontend/templates/config.html`, `frontend/templates/partials/openai_model_field.html`, `frontend/templates/partials/config_modal.html`, `frontend/templates/partials/config_feedback.html`, `frontend/static/style.css` - Introduce the config page, move global config off the topbar modal, and keep non-config screens model-only.
  ```text
  Function: page rendering and HTMX partial composition

  Input validation:
    - Config page always receives current OpenAI settings
    - Agent modal receives an existing agent plus the available model list

  Logic flow:
    1. Add a dedicated navigation entry for config.
    2. Replace the old global modal entry point with a link to the config page.
    3. Render test feedback and model options inline on the config page.
    4. Keep only the per-agent `Change model` button on agent screens.

  Return: full HTML pages plus targeted modal/page partials

  Edge cases:
    - No fetched models yet -> show empty/help state with current default model fallback
    - API test succeeds after a previous failure -> replace stale feedback cleanly

  Dependencies: Jinja templates, HTMX, app shell JS
  ```

### Phase 3: Remove Job Finder From Active Runtime

- [x] [MODIFIED] `backend/main.py`, `backend/agents/_registry.py`, `config/settings.yaml`, `tests/test_app.py`, `docs/ai/planning/epic-ai-agent-tool.md`, `docs/ai/requirements/req-ai-agent-tool.md`, `docs/ai/project/PROJECT_STRUCTURE.md`; [DELETED] `backend/api/job_finder.py`, `frontend/templates/job_finder.html`, `frontend/templates/partials/job_finder_filters.html`, `frontend/templates/partials/job_cards.html`, `frontend/templates/partials/job_run_feedback.html`, `frontend/templates/partials/openai_config_modal.html` - Remove Job Finder from active routing, default settings, tests, and planning references while preserving the remaining agents.
  ```text
  Function: app startup, registry discovery, smoke tests

  Input validation:
    - Registry only initializes agent packages that exist in active settings
    - Tests use the reduced active-agent fixture

  Logic flow:
    1. Stop mounting the Job Finder router.
    2. Ensure discovery skips packages that are no longer present in `settings.yaml`.
    3. Remove Job Finder expectations from dashboard/config/tests and add a regression check that its page now 404s.
    4. Sync epic/requirement docs with the new feature plan and removal outcome.

  Return: reduced active runtime with passing focused tests

  Edge cases:
    - Legacy local settings still contain `job_finder` -> inactive package may remain on disk, but the app should only expose configured agents
    - Stream and dashboard tests should still pass with the remaining agents

  Dependencies: FastAPI router setup, registry discovery, pytest
  ```

## 7. Follow-ups
- [ ] Delete the dormant `backend/agents/job_finder/` implementation if the repository no longer needs it as a reference slice.
