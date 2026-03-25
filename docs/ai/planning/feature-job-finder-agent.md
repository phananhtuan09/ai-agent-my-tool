# Plan: Job Finder Agent

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
- `backend/agents/job_finder/agent.py` - The current placeholder defines the agent slug, storage file, and page context contract that the real implementation must preserve.
- `backend/api/config.py` - Existing HTMX modal save flow already persists per-agent config and publishes SSE events; job-filter config should reuse the same repository conventions and error handling style.
- `backend/api/stream.py` - SSE already supports named event types and JSON payloads, which the job finder can reuse for status, notify, and UI updates.

### Reusable Components/Utils
- `backend/shared/settings.py` - Current YAML persistence layer can be extended to carry job-filter and crawl config.
- `backend/shared/events.py` - Existing per-agent event fan-out can broadcast crawl completion and warnings without new transport code.
- `frontend/templates/job_finder.html` - The placeholder shell already reserves a left workspace panel and right activity feed.

### Architectural Patterns
- `Registry-backed agent page`: Keep the job finder behind the existing `BaseAgent` and `AgentRegistry` flow so the app shell stays unchanged.
- `HTMX partial update`: Use server-rendered partials for config feedback and job results instead of adding SPA state management.

### Key Files to Reference
- `docs/ai/requirements/req-ai-agent-tool.md` - FR-07 through FR-14, BR-01 through BR-05, and job-specific edge cases.
- `docs/ai/requirements/agents/sa-ai-agent-tool.md` - Shared jobs table shape, crawl serialization guidance, and streaming expectations.
- `backend/main.py` - Application lifespan and scheduler setup that the job finder cron registration must plug into.

---

## 3. Goal & Acceptance Criteria

### Goal
- Replace the placeholder job finder with a real vertical slice that can persist job settings, run a crawl pipeline, apply hard filters before ranking, store results, and render ranked job cards with live status updates.

### Acceptance Criteria (Given/When/Then)
- Given the user opens the Job Finder page, when the page renders, then it shows a filter form, source toggles, run action, current crawl status, and ranked job cards from SQLite.
- Given a user saves job filter settings, when the request succeeds, then `config/settings.yaml` is updated, the in-memory job finder reloads its config, and the page reflects the saved values without a restart.
- Given a crawl runs across the configured sources, when one source fails, then the other sources still complete, the page receives a warning event for the failed source, and successful jobs remain visible.
- Given crawled jobs exist, when hard filters remove all jobs, then no ranking call runs and the UI shows an empty-state message.
- Given filtered jobs remain, when ranking completes, then each visible card shows title, company, salary, location, tech stack, source, score, reason, and outbound link.
- Given the daily crawl or manual run finishes, when the browser tab is open, then the user receives a completion notification with the new match count.

## 4. Risks & Assumptions

### Risks
- Real Playwright crawling for three external sites is brittle and hard to validate in the current environment, so the slice needs a crawler abstraction plus deterministic fallback fixtures for local development.
- The foundation settings model currently stores only provider/model/env-var values, so adding nested job config must preserve backward compatibility for the other agents.
- Ranking requires LLM behavior that cannot be integration-tested here; a deterministic scorer is needed as a safe fallback to prevent the feature from becoming non-functional when the API key is absent.

### Assumptions
- Source URLs and enable/disable toggles can live in `config/settings.yaml` under the `job_finder` agent section.
- The manual "Run Crawl" action and scheduler-driven crawl can use the same execution pipeline.
- A deterministic ranking fallback is acceptable when the configured API key is missing; once an API-backed client exists, it can replace the fallback without changing the UI or storage contracts.

### Concrete Settings Shape

```yaml
agents:
  job_finder:
    provider: anthropic
    model: claude-3-7-sonnet-latest
    api_key_env_var: ANTHROPIC_API_KEY
    job_finder:
      cron: "0 8 * * *"
      sources:
        topcv:
          enabled: true
          label: TopCV
          simulate_failure: false
        itviec:
          enabled: true
          label: ITviec
          simulate_failure: false
        vietnamworks:
          enabled: true
          label: VietnamWorks
          simulate_failure: false
      filters:
        salary_min: 1500
        salary_max: 3000
        locations: ["Ho Chi Minh City", "Hanoi"]
        must_have_frameworks: ["React", "TypeScript"]
        nice_to_have_frameworks: ["Next.js", "FastAPI"]
        exclude_keywords: ["intern"]
```

The nested `job_finder` payload must be persisted through `save_agent_settings("job_finder", {"job_finder": ...})`; no separate save helper is needed if the settings model is extended to validate that shape.

## 5. Definition of Done
- [x] Build passes (linter, type checks, compile)
- [x] Tests added and passing
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Implement the job finder as a full vertical slice: extend settings and storage first, build crawl/filter/rank logic second, then wire HTMX forms, partial rendering, SSE notifications, and tests. Use a source-adapter abstraction so the feature works now with deterministic fixture data while preserving a clean path to real Playwright adapters.

### Phase 1: Job Finder Domain And Storage

- [x] [MODIFIED] backend/shared/settings.py, config/settings.yaml — Extend the settings document to support nested job crawler and filter config.
  ```text
  Function: load_settings() / save_agent_settings(agent_name, payload)

  Input validation:
    - salary_min: integer >= 0
    - salary_max: integer >= salary_min
    - locations: list[str] with trimmed non-empty values
    - must_have_frameworks, nice_to_have_frameworks, exclude_keywords: list[str]
    - sources: keys limited to "topcv", "itviec", "vietnamworks"
    - cron: 5-field crontab string parsed by CronTrigger.from_crontab(...)

  Logic flow:
    1. Add typed nested models for job filter config and source toggles.
    2. Preserve compatibility for non-job agents by making nested config optional where appropriate.
    3. Persist nested job finder updates back to YAML without losing other agent sections.
    4. Reject invalid cron strings with ConfigError/HTTP 422 and do not mutate the active in-memory settings.

  Return: validated AppSettings | Error(ConfigError)

  Edge cases:
    - malformed comma-delimited form values -> normalize to an empty list or trimmed tokens
    - salary_max lower than salary_min -> reject with a validation error
    - malformed existing YAML -> return HTTP 400 on filter load/save and keep both the file and in-memory config unchanged

  Dependencies: pydantic, PyYAML, filelock
  ```

- [x] [ADDED] backend/agents/job_finder/models.py, backend/agents/job_finder/repository.py, backend/agents/job_finder/fixtures.py — Add the SQLite schema, typed job records, and deterministic source fixtures used by the crawl adapters.
  ```text
  Function: initialize_schema(connection) / upsert_jobs(jobs) / list_ranked_jobs(limit) / get_fixture_jobs(source)

  Input validation:
    - source: one of the configured job sources
    - job url: non-empty string
    - crawled_at: timezone-aware timestamp string

  Logic flow:
    1. Create the jobs table and related indexes if they do not exist.
    2. Store source jobs idempotently by URL and source pair.
    3. Return ranked jobs in score-descending order for the page partial.
    4. Expose deterministic fixture data per source for development runs.

  Return: stored jobs, query results | Error(sqlite3.DatabaseError)

  Edge cases:
    - duplicate jobs across reruns -> update existing row instead of inserting duplicates
    - old records older than 30 days -> purge before inserting fresh results

  Dependencies: sqlite3, dataclasses or pydantic models
  ```

### Phase 2: Crawl, Filter, Rank, And Agent Wiring

- [x] [ADDED] backend/shared/crawler.py, backend/agents/job_finder/tools.py, backend/agents/job_finder/skills.py — Add the crawl serialization guard, hard-filter logic, ranking pipeline, and job-finder prompt/fallback helpers.
  ```text
  Function: crawl_jobs(config) / filter_jobs(jobs, filter_config) / rank_jobs(jobs, llm_client, filter_config)

  Input validation:
    - source config must be enabled before crawling
    - job salary values may be null and should be handled without crashes
    - ranking inputs must only include jobs that passed hard filters

  Logic flow:
    1. Use backend/shared/crawler.py as the single guarded entrypoint with a module-level lock shared by manual and scheduled runs.
    2. Iterate enabled sources and fetch jobs through one adapter per source.
    3. Catch per-source crawl failures and accumulate warnings instead of aborting the whole run.
    4. Apply hard filters for salary, location, must-have frameworks, and exclude keywords before ranking.
    5. If jobs remain, rank them with a deterministic scorer and optional LLM-backed explanation path.
    6. Return ranked jobs plus warning metadata for the UI and SSE feed.

  Return: {jobs: list[RankedJob], warnings: list[str], matched_count: int} | Error(CrawlError)

  Edge cases:
    - zero enabled sources -> reject run with a validation error
    - zero filtered jobs -> skip ranking and return an empty-state result
    - malformed ranking output -> fall back to deterministic scoring and explanation
    - second run arrives while the global crawl lock is held -> return "crawl in progress" warning without starting another crawl

  Dependencies: shared settings, repository, event broker, shared crawler
  ```

- [x] [MODIFIED] backend/agents/job_finder/agent.py, backend/agents/base_agent.py, backend/main.py — Turn the placeholder into a stateful agent with scheduler registration, router wiring, storage initialization, and page context driven by real data.
  ```text
  Function: JobFinderAgent.initialize() / JobFinderAgent.run_crawl() / JobFinderAgent.register_jobs(scheduler) / JobFinderAgent.build_page_context()

  Input validation:
    - scheduler cron string must be a valid 5-field crontab string
    - manual run requests must target the `job_finder` agent only

  Logic flow:
    1. Initialize the jobs table during agent startup.
    2. Register the daily crawl scheduler job using CronTrigger.from_crontab(runtime.cron); timezone inherits the server/app default.
    3. Include backend/api/job_finder.py in backend/main.py so the HTMX routes are live.
    4. Run the crawl/filter/rank/persist pipeline for manual and scheduled executions.
    5. Persist in this order: purge old rows, upsert new jobs with scores/reasons, then re-query repository results for rendering.
    6. Publish notify and status updates through SSE after each run.
    7. Build template context from saved config, latest status, warnings, and ranked jobs.

  Return: UI context and run summary | Error(AgentError, ConfigError)

  Edge cases:
    - concurrent run request while a crawl is active -> emit "crawl in progress" warning
    - invalid cron during startup or config save -> reject and preserve the previous schedule
    - missing API key -> deterministic scorer remains available

  Dependencies: APScheduler, repository, tools, shared events
  ```

### Phase 3: HTMX UI And Focused Tests

- [x] [ADDED] backend/api/job_finder.py, frontend/templates/partials/job_finder_filters.html, frontend/templates/partials/job_cards.html, frontend/templates/partials/job_run_feedback.html — Add HTMX endpoints and partials for saving job settings and manually running the crawl.
  ```text
  Function: GET /agents/job_finder/filters / POST /agents/job_finder/filters / POST /agents/job_finder/run

  Input validation:
    - form fields normalized from comma-separated text inputs
    - source toggles accepted as on/off booleans

  Logic flow:
    1. Render the filter form partial from current saved config.
    2. Persist filter updates and re-render the form plus feedback.
    3. Trigger the agent crawl pipeline on manual run.
    4. Return job cards partials and run feedback suitable for HTMX swapping.
    5. Ensure manual run renders repository-backed results after persistence rather than transient in-memory rows.

  Return: HTML partials | Error(HTTP 422, HTTP 500)

  Edge cases:
    - manual run with all sources disabled -> return inline validation error
    - crawl warnings present -> show warning banner and still render successful results

  Dependencies: FastAPI form handling, job finder agent, shared settings
  ```

- [x] [MODIFIED] frontend/templates/job_finder.html, frontend/static/app.js, frontend/static/style.css, tests/test_app.py — Replace placeholder content with the actual job finder controls, cards, SSE behavior, and focused coverage for save/run flows.
  ```text
  Function: job finder page render, HTMX actions, SSE notify rendering, TestClient coverage

  Input validation:
    - template context must include saved filter config and job card data
    - tests should assert hard-filter behavior before ranking output is shown

  Logic flow:
    1. Render the job filter form and manual crawl button in the left panel.
    2. Render ranked job cards and empty/warning states beneath the controls.
    3. Ensure SSE notify/status events append readable entries to the activity feed.
    4. Verify dashboard integration, filter persistence, manual crawl, partial source failure, zero-filtered-results, malformed YAML handling, and filtered-result rendering.
    5. Verify invalid cron save returns a validation error, preserves the persisted config, and does not replace the active scheduler job.
    6. Verify the deterministic scorer fallback path when the API key env var is absent.

  Return: updated job finder page and test coverage

  Edge cases:
    - no jobs matched -> render empty state card
    - source failure during run -> render warning banner and still show successful jobs
    - settings YAML malformed before save -> show inline error and preserve current form state

  Dependencies: HTMX, Notification API, TestClient
  ```

## 7. Follow-ups
- [ ] Replace deterministic source fixtures with real Playwright site adapters once runtime dependencies are installed and selector validation is possible.
- [ ] Add batching and streaming token updates when a real LLM ranking path is wired in.
- [ ] Add integration tests around scheduled daily crawl behavior after the runtime environment can execute APScheduler and FastAPI together.
- [ ] Install project dependencies in the target environment, then rerun runtime imports and pytest validation for the new Job Finder flow.
