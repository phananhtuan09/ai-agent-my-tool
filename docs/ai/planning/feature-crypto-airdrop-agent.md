# Plan: Crypto Airdrop Agent

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
- `backend/agents/job_finder/agent.py` - Demonstrates the current crawl pipeline, scheduler registration, SSE publishing, and repository-backed page context pattern.
- `backend/agents/daily_scheduler/agent.py` - Shows how chat interactions, timeline-style UI refreshes, and scheduler jobs are already wired through HTMX and SSE.

### Reusable Components/Utils
- `backend/shared/settings.py` - Already supports nested agent runtime settings with cron validation, which is the right place to add configurable airdrop sources.
- `backend/shared/crawler.py` - Provides the global crawl serialization guard that this slice should reuse for 6-hour crawl execution.
- `frontend/static/app.js` - Already knows how to process specialized `ui_update` payloads, so the airdrop result grid and filter transcript should plug into the same client shell.

### Architectural Patterns
- `Registry-backed scheduled agent`: Keep the airdrop feature inside the existing `BaseAgent` and `AgentRegistry` flow so startup, sidebar, config modal, and SSE infrastructure remain unchanged.
- `Fixture-first crawler adapter`: Follow the Job Finder approach by separating crawl adapters/fixtures from ranking and persistence so source updates remain cheap.

### Key Files to Reference
- `docs/ai/requirements/req-ai-agent-tool.md` - Source of FR-22 through FR-27, BR-03, BR-04, BR-06, and the airdrop acceptance scenario.
- `docs/ai/requirements/agents/sa-ai-agent-tool.md` - Defines the `crawl_cycles` and `airdrops` table shape plus the planned 6-hour cron and chat pattern.
- `frontend/templates/crypto_airdrop.html` - Existing placeholder shell that should become the real split result/filter experience.

---

## 3. Goal & Acceptance Criteria

### Goal
- Replace the Crypto Airdrop placeholder with a real vertical slice that can crawl configurable sources, score airdrops with a deterministic rubric, retain only the latest 10 crawl cycles, and let the user filter or ask about the current ranked list through chat.

### Acceptance Criteria (Given/When/Then)
- Given the user opens the Crypto Airdrop page, when the page renders, then it shows source controls, a manual crawl action, a ranked airdrop card grid, and a chat/filter lane backed by SQLite.
- Given the 6-hour crawl or a manual run executes, when the enabled sources are processed, then results are stored under a new crawl cycle, sorted by score descending, and older cycles beyond the latest 10 are purged.
- Given one configured source fails, when the run completes, then the page still shows successful results and the activity feed displays a warning for the failed source.
- Given an airdrop record is visible, when the ranking pipeline completes, then the card shows the name, chain, score, requirements summary, deadline, and source link.
- Given the user sends a chat filter such as `show only Ethereum airdrops`, when the agent handles the message, then the card grid re-renders to the filtered subset and the assistant confirms the applied filter.
- Given browser notifications are enabled and a crawl finishes while the tab is open, when the agent publishes the completion event, then the browser shows a summary notification with the new ranked count.

## 4. Risks & Assumptions

### Risks
- Real external crawling is still environment-sensitive, so the first pass should keep source adapters fixture-backed and deterministic while preserving a clean path to later Playwright replacements.
- The current `LLMClient` does not execute real completions, so the scoring and analysis path must remain fully usable without live API keys.
- Free-text chat can drift into unsupported questions unless the first pass keeps the interaction contract narrow and explicit around filters and result summaries.
- `DeFiLlama` may challenge lightweight HTTP requests, so the source adapter needs a warning-backed fallback path until a browser-grade crawler is introduced.

### Assumptions
- The initial source list is `airdrops.io`, `CryptoRank`, and `DeFiLlama`, and each source should stay configurable in `settings.yaml` so you can change the list later without restructuring the code.
- A deterministic rubric based on chain, task difficulty, community signal, and deadline proximity is acceptable until a real LLM analysis path is added.
- Chat filtering can focus on chain, source, and keyword matching in Phase 1; richer Q&A can build on the same transcript and repository contracts later.

### Concrete Settings Shape

```yaml
agents:
  crypto_airdrop:
    provider: openai
    model: gpt-5
    api_key_env_var: OPENAI_API_KEY
    crypto_airdrop:
      cron: "0 */6 * * *"
      sources:
        airdrops_io:
          enabled: true
          label: airdrops.io
          url: https://airdrops.io
          simulate_failure: false
        cryptorank:
          enabled: true
          label: CryptoRank
          url: https://cryptorank.io
          simulate_failure: false
        defillama:
          enabled: true
          label: DeFiLlama
          url: https://defillama.com
          simulate_failure: false
```

The nested `crypto_airdrop` payload should round-trip through `save_agent_settings("crypto_airdrop", {"crypto_airdrop": ...})`, and new sources should require only a settings entry plus one fixture/adapter function.

## 5. Definition of Done
- [x] Build passes (linter, type checks, compile)
- [x] Tests added and passing
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Implement the Crypto Airdrop slice in three passes: add nested runtime settings plus cycle-based persistence first, wire the crawl/filter/rank/chat workflow second, then replace the placeholder UI with a live result grid and focused test coverage. Keep source adapters modular so the source list remains easy to update later.

### Phase 1: Runtime Settings And Cycle Persistence

- [x] [MODIFIED] `backend/shared/settings.py`, `config/settings.yaml` - Add typed runtime settings for configurable airdrop sources and the 6-hour cron.
  ```text
  Function: load_settings() / save_agent_settings(agent_name, payload)

  Input validation:
    - cron: valid 5-field crontab string
    - sources: keys limited to configured adapter names
    - label, url: non-empty strings
    - simulate_failure: boolean

  Logic flow:
    1. Add nested models for the crypto airdrop runtime config.
    2. Validate cron and source metadata while preserving compatibility for the other agents.
    3. Persist nested source updates back to YAML without dropping sibling sections.
    4. Reject invalid source config without mutating the current file.

  Return: validated AppSettings | Error(ConfigError)

  Edge cases:
    - malformed YAML -> keep the file unchanged and raise ConfigError
    - all sources disabled -> runtime save still succeeds, but crawl execution should reject later
    - unsupported source key -> reject during validation

  Dependencies: pydantic, PyYAML, filelock, APScheduler CronTrigger
  ```

- [x] [ADDED] `backend/agents/crypto_airdrop/models.py`, `backend/agents/crypto_airdrop/repository.py`, `backend/agents/crypto_airdrop/fixtures.py`, `backend/agents/crypto_airdrop/skills.py` - Add typed airdrop records, cycle retention helpers, fixture data, and deterministic scoring/explanation helpers.
  ```text
  Function: initialize() / start_cycle() / replace_cycle_airdrops(cycle_id, airdrops) / list_latest_airdrops(limit) / get_fixture_airdrops(source) / score_airdrop(record)

  Input validation:
    - source: one of "airdrops_io" | "cryptorank" | "defillama"
    - name, url: non-empty strings
    - chain: normalized non-empty string
    - crawl cycle id: integer > 0

  Logic flow:
    1. Create `crawl_cycles` and `airdrops` tables with indexes.
    2. Insert a new crawl cycle for each execution and store ranked airdrops under that cycle.
    3. Purge the oldest cycle once more than 10 cycles are retained.
    4. Expose deterministic fixture data and rubric helpers per source.

  Return: ranked airdrop rows and cycle metadata | Error(sqlite3.DatabaseError)

  Edge cases:
    - duplicate records across sources -> keep them as separate rows because source links differ
    - no stored rows -> return empty-state data
    - malformed deadline data -> store null and keep scoring deterministic

  Dependencies: sqlite3, datetime, dataclasses
  ```

### Phase 2: Crawl, Rank, Chat Filter, And Agent Wiring

- [x] [ADDED] `backend/agents/crypto_airdrop/tools.py` and [x] [MODIFIED] `backend/agents/crypto_airdrop/agent.py`, `backend/main.py` - Implement the crawl pipeline, chat filter handling, scheduler registration, and live result publication.
  ```text
  Function: run_airdrop_pipeline(runtime, llm_client, trigger) / handle_chat(message) / run_crawl(trigger) / register_jobs(scheduler)

  Input validation:
    - at least one source must be enabled before a crawl
    - chat message: trimmed non-empty string
    - filter grammar supports source names, chain names, and keyword phrases

  Logic flow:
    1. Serialize crawl execution through `shared/crawler.py`.
    2. Iterate enabled sources, gather fixture-backed rows, and continue on per-source CrawlError.
    3. Score each record, generate deterministic reasoning, and persist them under a new cycle.
    4. Re-query the latest ranked rows for rendering and notification payloads.
    5. Handle chat messages by storing the transcript, applying a filter to the latest cycle, and publishing updated UI state.
    6. Register the 6-hour cron job and reuse the same run path for manual and scheduled crawls.

  Return: run summary / chat result payload | Error(ConfigError, CrawlError)

  Edge cases:
    - all enabled sources fail -> return warnings and an empty ranked list without crashing
    - missing API key -> deterministic fallback stays active
    - unsupported filter text -> respond with guidance instead of mutating stored results

  Dependencies: shared crawler, repository, skills, fixtures, EventBroker
  ```

- [x] [ADDED] `backend/api/crypto_airdrop.py`, `frontend/templates/partials/crypto_airdrop_controls.html`, `frontend/templates/partials/airdrop_cards.html`, `frontend/templates/partials/crypto_airdrop_chat.html`, `frontend/templates/partials/crypto_airdrop_run_feedback.html` - Add HTMX endpoints and partials for source settings, manual crawl, and chat filtering.
  ```text
  Function: GET /agents/crypto_airdrop/controls / POST /agents/crypto_airdrop/settings / POST /agents/crypto_airdrop/run / POST /agents/crypto_airdrop/chat

  Input validation:
    - source toggles accepted as on/off booleans
    - chat messages reject blank input
    - settings only persist valid source metadata and cron strings

  Logic flow:
    1. Render the source settings partial from current saved config.
    2. Persist source toggles and cron updates, then re-register scheduler jobs.
    3. Trigger the crawl pipeline on manual run and return refreshed cards plus feedback.
    4. Handle chat filter messages and return a refreshed chat transcript plus card grid.

  Return: HTML partials | Error(HTTP 400, HTTP 422, HTTP 500)

  Edge cases:
    - all sources disabled -> inline validation error
    - crawl warnings present -> show warning banner and successful results together
    - no results match the chat filter -> return a clear empty state

  Dependencies: FastAPI form handling, CryptoAirdropAgent, shared settings
  ```

### Phase 3: Result UI, SSE Rendering, And Validation

- [x] [MODIFIED] `frontend/templates/crypto_airdrop.html`, `frontend/static/app.js`, `frontend/static/style.css` - Replace the placeholder layout with live airdrop controls, ranked cards, and chat/filter rendering.
  ```text
  Function: crypto airdrop page render / renderAirdropResults(payload)

  Input validation:
    - template context includes source settings, airdrop rows, and chat transcript
    - SSE payload includes JSON-safe ranked row fields

  Logic flow:
    1. Render source toggles and crawl actions in the left panel.
    2. Render ranked airdrop cards with chain, score, summary, deadline, and source link.
    3. Render the chat/filter transcript and composer in the right panel.
    4. Extend `app.js` to update the card grid and transcript when `ui_update` events arrive.

  Return: updated airdrop UI shell and live refresh behavior

  Edge cases:
    - no rows stored yet -> meaningful empty state
    - filtered result empty -> targeted empty state instead of blank panel
    - notifications denied -> in-page feed still shows crawl completion

  Dependencies: HTMX, Notification API, existing app shell
  ```

- [x] [MODIFIED] `tests/test_app.py` - Add focused coverage for config persistence, manual crawl, cycle retention, partial source failure, and chat filtering.
  ```text
  Function: TestClient coverage for Crypto Airdrop routes and pipeline

  Input validation:
    - cron strings must remain valid
    - deterministic filter assertions should pin source and chain filtering outcomes

  Logic flow:
    1. Verify the page renders controls and empty state.
    2. Verify manual crawl persists ranked airdrop cards.
    3. Verify source failure still returns successful rows from other sources.
    4. Verify chat filtering narrows the latest cycle by chain or source.
    5. Verify invalid cron or malformed YAML returns the expected inline errors.

  Return: passing coverage for the crypto slice

  Edge cases:
    - all sources disabled -> 422 feedback
    - no filter match -> empty result state
    - more than 10 cycles stored -> oldest cycle is purged

  Dependencies: FastAPI TestClient
  ```

## 7. Follow-ups
- [ ] Replace the remaining `DeFiLlama` fallback path with a browser-grade crawler or a compliant API-backed fetch once the runtime environment supports it.
- [ ] Add richer chat Q&A that can summarize or compare current airdrops beyond simple filter requests.
- [ ] Add web search augmentation once a dedicated `shared/web_search.py` path exists in the runtime environment.
