# Plan: OpenAI Global Config

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

### Similar Features
- `backend/api/config.py` - Existing HTMX modal flow for per-agent provider/model configuration that can be split into global OpenAI config and model-only overrides.
- `backend/shared/settings.py` - YAML persistence layer already supports typed validation, partial updates, and file locking.

### Reusable Components/Utils
- `frontend/templates/partials/config_feedback.html` - Shared success and error feedback partial for modal form submissions.
- `frontend/static/app.js` - Live snapshot updates for model/status badges after config hot-swap events.

### Architectural Patterns
- `Registry-backed hot swap`: Agents are reloaded in memory after `settings.yaml` changes and publish SSE status events without restarting the app.
- `Shared settings document`: Runtime config is persisted centrally in `config/settings.yaml`, while secrets are expected to stay in `config/.env`.

### Key Files to Reference
- `backend/shared/llm_client.py` - Current model/provider descriptor that must become OpenAI-only and use effective model resolution.
- `backend/agents/base_agent.py` - Snapshot shape and runtime reload contract used by dashboard, SSE, and agent pages.
- `frontend/templates/base.html` - Topbar entry point for the new global config menu and the per-agent model-only modal.

---

## 3. Goal & Acceptance Criteria

### Goal
- Replace the current per-agent multi-provider config flow with an OpenAI-only configuration model that keeps `base_url`, `api_key`, and `default_model` global while allowing each agent page to override only its own model.

### Acceptance Criteria (Given/When/Then)
- Given the app starts with valid settings, when the dashboard or an agent page renders, then the UI no longer exposes provider selection and only references OpenAI configuration.
- Given a user opens the global config menu, when they save a new `base_url`, `default_model`, and optional replacement `api_key`, then `config/settings.yaml` persists the non-secret values, `config/.env` persists `OPENAI_API_KEY`, the current process updates `os.environ`, and all agents hot-swap without an app restart.
- Given an agent has no explicit model override, when the global `default_model` changes, then that agent immediately reports and uses the new default model in snapshots and UI badges.
- Given a user opens an agent page model dialog, when they save a model override or clear it back to default, then only that agent’s model selection changes while global `base_url` and `api_key` remain untouched.

## 4. Risks & Assumptions

### Risks
- Writing secrets from the UI introduces persistence and masking concerns, so the modal must avoid echoing the saved API key back into HTML responses.
- Existing routes that call `save_agent_settings()` also need the registry’s in-memory root settings refreshed, or future reloads can drift from disk.
- `default_model` loses practical value if every agent stores a required explicit model, so agent-level model overrides must become optional.

### Assumptions
- OpenAI is now the only supported provider, and removing Anthropic-specific config fields is in scope.
- Persisting `OPENAI_API_KEY` into `config/.env` is acceptable for this project as long as the file remains gitignored and the running process is updated immediately.
- A small curated model menu is sufficient for the UI; users do not need free-text model entry in this slice. The canonical list for this slice is `gpt-5`, `gpt-5-mini`, and `gpt-4.1-mini`, exposed from one shared backend constant and reused by routes, templates, and tests.

## 5. Definition of Done
- [x] `python3 -m compileall backend tests` passes
- [x] Tests added and passing
- [x] `pytest tests/test_app.py` passes
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Split configuration into two layers: global OpenAI connection settings on the app and optional per-agent model overrides. Keep the existing HTMX modal interaction model, but move the global connection form into its own menu and reduce agent-specific configuration to model selection only.

### Phase 1: Settings And Runtime Contract

- [x] [MODIFIED] backend/shared/settings.py, backend/shared/llm_client.py — Introduce global `OpenAISettings`, optional per-agent model overrides, and helpers for persisting `OPENAI_API_KEY` into `config/.env`.
  ```text
  Function: load_settings() / save_openai_settings(payload, api_key) / save_agent_settings(agent_name, payload) / LLMClient.from_settings(agent_settings, openai_settings)

  Input validation:
    - openai.base_url: non-empty URL string
    - openai.default_model: non-empty string from the supported menu values
    - api_key: optional on save; when present must be non-empty after trim
    - agent.model: nullable string; blank input is normalized to null

  Logic flow:
    1. Extend the root YAML schema to include an `openai` section plus agent-level optional `model`.
    2. Resolve an agent's effective model as `agent.model or openai.default_model`.
    3. Keep API key secrets out of YAML and instead update `config/.env` with `OPENAI_API_KEY`.
    4. Save global config by preparing the updated YAML payload first, then writing `.env`, then writing `settings.yaml`; if the YAML write fails after `.env` changes, restore the previous `.env` content before surfacing the error.
    5. Apply the new API key to `os.environ` immediately so hot-swap works without restart.

  Return: validated AppSettings / LLM summary / Error(ConfigError)

  Edge cases:
    - Missing `.env` file -> create it safely
    - Blank API key field on save -> preserve current key
    - Malformed YAML or invalid model payload -> reject without partial write
    - Legacy settings with `provider` / `api_key_env_var` still present -> fail fast with a clear validation error and require the repo's updated default settings file rather than attempting silent migration

  Dependencies: pydantic, yaml, filelock, os, pathlib
  ```

- [x] [MODIFIED] backend/agents/_registry.py, backend/agents/base_agent.py, backend/agents/job_finder/__init__.py, backend/agents/daily_scheduler/__init__.py, backend/agents/crypto_airdrop/__init__.py, backend/agents/job_finder/agent.py, backend/agents/daily_scheduler/agent.py, backend/agents/crypto_airdrop/agent.py — Push global OpenAI settings through the registry and agent runtime reload path.
  ```text
  Function: AgentRegistry.get_openai_settings() / AgentRegistry.replace_settings(settings) / BaseAgent.reload_settings(agent_settings, openai_settings)

  Input validation:
    - AppSettings must contain both `openai` and all required agent keys
    - agent slug lookup must still 404 for unknown agents

  Logic flow:
    1. Store the latest root settings object in the registry after each save.
    2. Pass global OpenAI settings into each agent on startup and reload.
    3. Publish refreshed snapshots using the effective model and OpenAI connection status.

  Return: hot-swapped agent instances and consistent registry state

  Edge cases:
    - Saving one agent's model override must not reset other agents
    - Saving global OpenAI settings must update all agents in one pass

  Dependencies: registry, shared settings, shared llm client
  ```

### Phase 2: Routes And UI Split

- [x] [MODIFIED] backend/api/config.py, backend/api/pages.py, frontend/templates/base.html, frontend/templates/partials/config_feedback.html — Add a global OpenAI config modal and keep modal feedback reusable.
  ```text
  Endpoint: GET|POST /config/openai

  Input validation:
    - base_url: required trimmed string
    - default_model: required option from the shared `SUPPORTED_OPENAI_MODELS` constant
    - api_key: optional password field; blank means keep current stored secret

  Logic flow:
    1. Render a global config modal from the top bar on all pages.
    2. Persist `base_url` and `default_model` to YAML, write `OPENAI_API_KEY` to `.env` when provided, and reload all agents.
    3. Return shared success/error feedback and emit status refresh events for active pages.

  Return: HTML modal or feedback partial | Error(HTTP 400, HTTP 422)

  Edge cases:
    - No new API key provided -> keep existing `.env` value
    - Invalid base URL or model -> inline validation failure

  Dependencies: FastAPI form handling, registry, shared settings helpers
  ```

- [x] [MODIFIED] backend/api/config.py, frontend/templates/partials/config_modal.html, frontend/templates/dashboard.html, frontend/templates/job_finder.html, frontend/templates/daily_scheduler.html, frontend/templates/crypto_airdrop.html, frontend/static/app.js — Reduce per-agent config to model-only selection and update UI labels/badges to OpenAI-only semantics.
  ```text
  Endpoint: GET|POST /agents/{agent_name}/config

  Input validation:
    - agent_name: must exist in registry
    - model: blank -> null override, otherwise one option from the shared `SUPPORTED_OPENAI_MODELS` constant

  Logic flow:
    1. Render a per-agent modal that edits only the agent's model override.
    2. Save blank input as `null` to inherit the global default model.
    3. Remove provider/env-var UI from cards and hero badges, and show effective model plus default/override state where helpful.
    4. Keep SSE-driven model/status updates working after save.

  Return: HTML partials and updated live snapshot state

  Edge cases:
    - Agent reset to default model -> badge updates immediately
    - Dashboard snapshot still loads when no API key exists

  Dependencies: Jinja templates, HTMX, AppShell update logic
  ```

### Phase 3: Defaults And Validation

- [x] [MODIFIED] config/settings.yaml, config/.env.example, tests/test_app.py — Refresh defaults for the new schema and add focused coverage for global config persistence plus per-agent model inheritance.
  ```text
  Function: pytest coverage for dashboard render, global config save, and per-agent override save

  Input validation:
    - Test settings fixture must match the new `openai` + `agents` schema
    - Temp `.env` fixture must isolate API key persistence from the real workspace

  Logic flow:
    1. Replace provider/env-var fields in default settings with the new global OpenAI block.
    2. Remove Anthropic examples from `.env.example`.
    3. Verify saving global config updates YAML, writes `.env`, and changes snapshots.
    4. Verify clearing an agent override falls back to `default_model`.
    5. Verify legacy `provider` / `api_key_env_var` fixture data now fails clearly instead of being silently accepted.

  Return: updated defaults and passing tests

  Edge cases:
    - Missing `.env` before save -> test helper confirms auto-create
    - Blank agent model override -> effective model comes from global default

  Dependencies: pytest, TestClient, temp paths
  ```

## 7. Follow-ups
- [ ] Replace the descriptor-only `LLMClient` with a real OpenAI SDK wrapper if future slices need live model calls, retries, or custom transport handling.
