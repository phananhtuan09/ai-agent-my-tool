# Requirement: AI Agent Tool Web Interface

> Generated: 2026-03-23
> Status: Draft
> Complexity: High

Note: All content in this document is in English.

---

## Quick Links

| Document | Status |
|----------|--------|
| [BA Analysis](agents/ba-ai-agent-tool.md) | ✅ Complete |
| [SA Assessment](agents/sa-ai-agent-tool.md) | ✅ Complete |
| [Domain Research](agents/research-ai-agent-tool.md) | ⏭️ Skipped (Light mode) |
| [UI/UX Design](agents/uiux-ai-agent-tool.md) | ⏭️ Skipped (Light mode) |

## Related Plans

- [Epic: AI Agent Tool Delivery](../planning/epic-ai-agent-tool.md)
- [Feature Plan: AI Agent Foundation](../planning/feature-ai-agent-foundation.md)
- [Feature Plan: Job Finder Agent](../planning/feature-job-finder-agent.md)
- [Feature Plan: Daily Schedule Agent](../planning/feature-daily-schedule-agent.md)
- [Feature Plan: Crypto Airdrop Agent](../planning/feature-crypto-airdrop-agent.md)

---

## 1. Executive Summary

A personal-use web interface hosted on a VPS that provides a unified entry point for three independent AI-powered automation tools: a job finder that crawls Vietnamese job sites daily and uses AI to filter and rank relevant listings; a daily schedule agent that accepts task input via chat, creates an optimized timeline, and sends hourly reminders; and a crypto airdrop agent that crawls airdrop listings every 6 hours and AI-ranks them by potential. Each tool operates independently with its own SQLite database, LLM configuration, and cron schedule. The web interface uses FastAPI + HTMX with Server-Sent Events for real-time streaming output. The agent registry pattern enables new tools to be added without touching core code.

---

## 2. Problem Statement

### Context
A developer needs to automate three recurring manual tasks: checking multiple job listing sites daily, planning and tracking daily coding tasks, and monitoring crypto airdrop opportunities across multiple sources.

### Problem
- Job hunting across TopCV, ITviec, and VietnamWorks is repetitive; no centralized filtering by salary, tech stack, or location exists.
- Daily task scheduling is manual with no AI-assisted time estimation or adaptive rescheduling.
- Crypto airdrop tracking requires frequent manual checks across multiple sites with no systematic potential evaluation.

### Impact
Without this tool, the developer spends significant manual effort on tasks that can be fully automated. There is no single interface to manage all three automation workflows.

---

## 3. Users & User Stories

### Target Users

| User Type | Description | Primary Goals |
|-----------|-------------|---------------|
| Developer (personal) | Single user on personal VPS | Automate job search, plan daily work, track airdrops |

### User Stories

| ID | Priority | As a... | I want to... | So that... |
|----|----------|---------|--------------|------------|
| US-01 | Must | Developer | Configure job search filters (salary, frameworks, location) | AI shows only relevant listings |
| US-02 | Must | Developer | Have jobs crawled daily automatically | I always have fresh listings without manual effort |
| US-03 | Must | Developer | Input daily tasks and get an AI-optimized schedule | I use my time efficiently |
| US-04 | Must | Developer | Receive hourly reminders to update task progress | I stay on track throughout the day |
| US-05 | Must | Developer | Chat with the scheduler to reschedule remaining tasks | The plan adapts to reality as the day progresses |
| US-06 | Must | Developer | Have airdrop data crawled every 6 hours and AI-analyzed | I see ranked airdrops without manual research |
| US-07 | Must | Developer | Chat with the airdrop agent to filter or ask questions | I can drill into specific airdrops interactively |
| US-08 | Must | Developer | Switch LLM provider/model per agent from the UI | I can optimize cost and performance per agent |
| US-09 | Should | Developer | Receive browser notification when cron jobs complete | I'm alerted to new results without polling |
| US-10 | Should | Developer | Add new agent tools without touching core code | The system is extensible |

---

## 4. Functional Requirements

### 4.1 Cross-Cutting

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-01 | Sidebar navigation with entry per agent | Must | Sidebar shows Job Finder, Daily Schedule, Crypto Airdrop |
| FR-02 | Per-agent LLM config modal (gear icon): provider, model, hot-swap | Must | Changes apply without server restart |
| FR-03 | Isolated SQLite memory.db per agent | Must | Agents never share DB files |
| FR-04 | SSE streaming for chat tokens and UI panel updates | Must | Text tokens stream to chat panel; tool call results update display panel in real-time |
| FR-05 | Browser Notification API on cron completion (tab must be open) | Must | Notification fires when tab is open; if tab closed, notification is lost (MVP) |
| FR-06 | Agent registry: new agent = new folder + register() | Should | Adding agent folder auto-appears in sidebar |

### 4.2 Find Job Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-07 | Daily cron crawls TopCV, ITviec, VietnamWorks (configurable) | Must | Cron runs daily; each source toggleable in config |
| FR-08 | Job filter config: salary range, must-have/nice-to-have frameworks, locations, exclude keywords | Must | Config saves to settings.yaml; hot-reloaded |
| FR-09 | Hard filter first: exclude jobs not matching salary + location + must-have keywords | Must | Non-matching jobs excluded entirely before AI |
| FR-10 | AI ranks filtered jobs with match score (0-100) and reason | Must | Each card shows score + AI reasoning |
| FR-11 | Job cards: title, company, salary, location, tech stack, source, score, link | Must | All fields visible; link opens source in new tab |
| FR-12 | 30-day data retention; auto-purge on each crawl | Must | Records older than 30 days deleted |
| FR-13 | Browser notification on crawl complete with new match count | Should | Notification shows count |
| FR-14 | Crawler failure: warn immediately, continue other sources | Must | Warning shown per failed source; results from successful sources displayed |

### 4.3 Daily Schedule Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-15 | Task input via chat (free-text, morning) | Must | Agent parses and confirms task list in chat |
| FR-16 | AI time estimation and optimized schedule rendered in timeline panel | Must | Timeline shows ordered tasks with start/end times |
| FR-17 | Split-panel layout: timeline (left) + chat (right) | Must | Both panels visible simultaneously |
| FR-18 | Hourly cron (configurable) sends reminder message in chat panel | Must | Agent message appears automatically in chat |
| FR-19 | User progress update via chat → agent reschedules remaining tasks from "now" | Must | Timeline re-renders with updated remaining tasks |
| FR-20 | Overdue tasks: agent flags in chat and asks user interactively what to do | Must | Agent waits for user decision before rescheduling |
| FR-21 | Today-only tasks; auto-cleared at midnight | Must | Tasks cleared by midnight APScheduler job |

### 4.4 Crypto Airdrop Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-22 | 6-hour cron (configurable) crawls airdrop sites | Must | Crawl runs on schedule; results in SQLite |
| FR-23 | AI analyzes each airdrop via predefined skill template (team, tokenomics, community, task/reward) | Must | Each airdrop has structured AI evaluation |
| FR-24 | Airdrop cards ranked by AI score: name, chain, score, requirements summary, deadline, source link | Must | Cards sorted by score DESC |
| FR-25 | Chat interface: user can ask questions or request filtering | Must | Agent responds and re-renders filtered list |
| FR-26 | Last 10 crawl cycles retained; oldest auto-purged | Must | On new crawl: delete oldest if > 10 stored |
| FR-27 | Crawler failure: warn immediately, continue other sources | Must | Same pattern as FR-14 |

---

## 5. Business Rules

| ID | Rule | Condition | Action |
|----|------|-----------|--------|
| BR-01 | Hard filter before AI ranking | After job crawl | Apply salary/location/keyword filter before any LLM call |
| BR-02 | Jobs failing hard filter are excluded | Job doesn't match mandatory criteria | Excluded entirely; not shown to user |
| BR-03 | Crawler failure = warn, not abort | Any source crawler fails | Log, warn, continue with other sources |
| BR-04 | No retry on crawler failure (MVP) | Crawler fails | Warn immediately; skip retries for simplicity |
| BR-05 | Job 30-day purge | Each crawl run | DELETE WHERE crawled_at < now() - 30 days |
| BR-06 | Airdrop 10-cycle purge | New crawl cycle completes | Delete oldest cycle_id if stored cycles > 10 |
| BR-07 | Schedule today-only | Midnight APScheduler job | DELETE FROM tasks |
| BR-08 | Overdue task interactive | task.end_time < now() and status != done | Agent flags in chat; waits for user decision |
| BR-09 | Model config hot-swap | User saves gear icon modal | New LLMClient instantiated in place; no restart |
| BR-10 | Agent registry auto-discovery | FastAPI startup | Registry scans agents/ dir; registers all valid agents |
| BR-11 | Playwright crawl serialized | Any crawl starts | asyncio.Lock in shared/crawler.py; max 1 browser session |
| BR-12 | Browser notification requires open tab | Cron completes | MVP constraint; tab-closed notifications lost |
| BR-13 | Agent memory isolation | At all times | Agents never read/write each other's memory.db |
| BR-14 | Airdrop criteria fixed in skill template (Phase 1) | Airdrop evaluation | Use predefined criteria; user cannot override in Phase 1 |

---

## 6. Technical Assessment

### Feasibility Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| Overall | ⚠️ Feasible with Changes | Playwright memory + anti-blocking require mitigation |
| Frontend | 🟡 Medium | SSE + HTMX integration; split-panel layouts; notification flow |
| Backend | 🔴 High | Concurrent Playwright + APScheduler + SSE in one process |
| Database | 🟢 Low | SQLite WAL mode sufficient for single-user tool |
| Crawler | 🔴 High | Anti-blocking for job sites; DuckDuckGo rate limits; unknown airdrop sites |
| LLM Integration | 🟡 Medium | Two SDKs unified; structured output parsing; hot-swap |

### Recommended Architecture

Layered Monolith with Agent Registry. Single FastAPI process; agents self-register on startup; per-agent asyncio Queue for SSE fan-out; Playwright runs in `asyncio.to_thread()` with global Lock to prevent OOM.

### Technology Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Backend | FastAPI 0.110+ | Async-native, SSE StreamingResponse, lifespan |
| ASGI | Uvicorn 0.27+ | Production async SSE |
| Frontend | HTMX 1.9+ + Jinja2 | hx-ext="sse"; no build pipeline; per conventions |
| Scheduler | APScheduler 3.10+ | AsyncIOScheduler; cron + interval triggers |
| Crawler | Playwright 1.40+ + playwright-stealth | JS-rendered pages; bot detection bypass |
| Web Search | duckduckgo-search 4.x | Free; no API key; rate-limit mitigation required |
| LLM | anthropic + openai (latest) | Dual-provider; streaming; hot-swap |
| Database | SQLite + aiosqlite 0.19+ | Per-agent isolation; WAL mode; async |
| Config | PyYAML + python-dotenv | settings.yaml + .env |

### Technical Risks

| ID | Risk | Impact | Likelihood | Mitigation |
|----|------|--------|------------|------------|
| TR-01 | VPS OOM: Playwright + concurrent crawls | High | High | asyncio.Lock serializes crawl sessions; benchmark on actual VPS before Phase 3 |
| TR-02 | Job sites block headless browser | High | High | playwright-stealth + random user-agent + delays; manual test each site before Phase 3 |
| TR-03 | DuckDuckGo library breaks | Medium | Medium | Pin version; fallback to analyze without web search |
| TR-04 | SSE generator leak on disconnect | Medium | Medium | try/finally cleanup in generator; catch GeneratorExit |
| TR-05 | LLM structured output parse failures | Medium | High | Pydantic validation + fallback rendering mandatory |
| TR-06 | Airdrop target sites unknown (OQ-02) | High | High | Phase 4 blocked; must confirm before starting |

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | LLM ranking batched (20 jobs/batch); partial results streamed progressively |
| **Security** | Jinja2 auto-escaping on all crawled content; settings.yaml chmod 600; API keys never logged |
| **Compatibility** | Desktop Chrome/Firefox; tab-open required for notifications (MVP) |
| **Concurrency** | One Playwright session at a time (asyncio.Lock); SQLite WAL for concurrent read/write |

---

## 8. Technical Edge Cases

| ID | Category | Edge Case | Expected Behavior | Priority |
|----|----------|-----------|-------------------|----------|
| TE-01 | Concurrency | Two crawl jobs fire simultaneously | asyncio.Lock serializes; second waits; "crawl in progress" notify | Must |
| TE-02 | Concurrency | Chat sent while cron LLM call running | is_processing flag; return "Agent is thinking..." | Must |
| TE-03 | Data | Zero jobs pass hard filter | Empty state card; skip AI ranking call | Must |
| TE-04 | Data | LLM returns malformed JSON | try/except; fallback to raw text; no crash | Must |
| TE-05 | Data | settings.yaml malformed | Catch yaml.YAMLError; return 400; keep last valid config | Must |
| TE-06 | Data | memory.db missing on startup | Auto-create via CREATE TABLE IF NOT EXISTS | Must |
| TE-07 | Network | Playwright timeout on job site | CrawlError; continue other sources; warn user | Must |
| TE-08 | Network | LLM API timeout / 5xx | Retry once after 3s; push error to SSE chat on failure | Must |
| TE-09 | Network | SSE connection drops mid-stream | GeneratorExit caught; Queue listener cleaned up | Must |
| TE-10 | Security | Crawled HTML contains XSS | Jinja2 auto-escaping; never use `\| safe` on crawled content | Must |
| TE-11 | Integration | DuckDuckGo rate-limited | Exponential backoff + jitter; cache per crawl cycle; skip after 3 retries | Must |
| TE-12 | State | Overdue task handling | Agent flags in LLM context; waits for user interactive decision in chat | Must |

---

## 9. Out of Scope (MVP)

- Multi-user / authentication
- Service Worker for tab-closed push notifications (Phase 2)
- Multi-day task history for Daily Schedule (Phase 2)
- Custom airdrop evaluation criteria via UI (Phase 2)
- Email / Telegram / Slack notifications
- Mobile-responsive design
- Automated job application submission
- Proxy rotation / CAPTCHA solving for job crawlers

---

## 10. Open Questions

| ID | Question | Owner | Status | Blocking |
|----|----------|-------|--------|----------|
| OQ-01 | Which specific airdrop sites to crawl? (airdrops.io? DeFiLlama? CryptoRank?) | Developer | Resolved — use airdrops.io, CryptoRank, and DeFiLlama for Phase 1 | No |
| OQ-02 | Does playwright-stealth bypass TopCV/ITviec/VietnamWorks bot detection? | Developer | Open | Yes — Phase 3 |
| OQ-03 | Gear icon modal: accept raw API key, or only reference env var names? | Developer | Open | No |
| OQ-04 | Missed hourly reminders when tab closed — queue and show on return? | Developer | Open | No |
| OQ-05 | Daily schedule: auto-reset at midnight, or require manual clear? | Developer | Open | No (recommend: auto) |

---

## 11. Acceptance Criteria

### Scenario 1: Job Finder — Daily Crawl and Filter

- **Given** daily cron fires at configured time
- **When** crawl completes on all configured sources
- **Then** jobs are hard-filtered by config, AI-ranked with scores, and displayed as cards; browser notification fires; failed sources show inline warning

### Scenario 2: Daily Schedule — Morning Task Input and Hourly Reminder

- **Given** user opens Daily Schedule page in the morning
- **When** user inputs task list in chat
- **Then** agent creates optimized timeline rendered in left panel; hourly cron fires reminder message in chat; user replies with progress and timeline re-renders

### Scenario 3: Daily Schedule — Overdue Task

- **Given** current time has passed a task's estimated end time
- **When** agent re-schedules after user progress update
- **Then** agent flags overdue task in chat and asks user what to do before rescheduling

### Scenario 4: Crypto Airdrop — 6-Hour Crawl and Chat Filter

- **Given** 6-hour cron fires
- **When** crawl and AI analysis complete
- **Then** ranked airdrop cards appear in display panel; user can chat "show only Ethereum airdrops" and agent re-renders filtered list

### Scenario 5: LLM Config Hot-Swap

- **Given** user clicks gear icon on any agent
- **When** user changes provider from Anthropic to OpenAI and saves
- **Then** next agent interaction uses new provider; no server restart required

### Scenario 6: Crawler Failure

- **Given** daily job crawl runs
- **When** one source (e.g., ITviec) fails with CrawlError
- **Then** warning card shows "ITviec failed"; results from TopCV and VietnamWorks display normally

---

## 12. Implementation Guidance

### Suggested Phases

| Phase | Focus | Priority | Prerequisite |
|-------|-------|----------|-------------|
| 1 | Foundation: LLMClient, BaseAgent, registry, SSE, base.html | High | None |
| 2 | Daily Schedule Agent: chat, schedule, hourly cron, timeline UI | High | Phase 1 |
| 3 | Job Finder Agent: Playwright crawlers, filter, AI ranking, config UI | High | Phase 1 + crawl test |
| 4 | Crypto Airdrop Agent: crawlers, analysis, 6h cron, chat UI | High | Phase 1 + OQ-01 resolved |
| 5 | LLM config modal, hot-swap, browser notifications, polish | Medium | Phases 2–4 |

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Anthropic API key | External | Required from Phase 1 |
| OpenAI API key | External | Required from Phase 1 |
| Confirm airdrop target sites (OQ-01) | Decision | Resolved — Phase 1 uses airdrops.io, CryptoRank, and DeFiLlama |
| Playwright-stealth crawl test on job sites (OQ-02) | Validation | Pending — blocks Phase 3 |
| VPS memory benchmark with Playwright | Validation | Pending — before Phase 3 |

---

## 13. Domain Glossary

| Term | Definition |
|------|------------|
| SSE | Server-Sent Events: one-way real-time stream from server to browser |
| APScheduler | Python background job scheduler; AsyncIOScheduler runs in FastAPI's event loop |
| Agent Registry | Pattern where agents self-register at startup; new agents added by folder creation |
| Hard Filter | Excludes records failing mandatory criteria entirely before any AI processing |
| AI Rank | LLM scores remaining records by relevance; sorted by score |
| Airdrop | Free token distribution by a crypto project to eligible wallet addresses |
| memory.db | Per-agent SQLite database; stores agent-specific data in isolation |
| Skill Template | Fixed prompt template encoding domain-specific evaluation criteria |
| asyncio.Lock | Python async primitive to serialize concurrent operations (e.g., Playwright sessions) |
| WAL mode | SQLite Write-Ahead Logging; allows concurrent reads while one writer is active |

---

## 14. Implementation Readiness Score

**Score**: 72%

| Criteria | Status | Weight |
|----------|--------|--------|
| All FRs have testable acceptance criteria | ✅ | 20% |
| No critical open questions | ❌ OQ-02 still blocking | 20% |
| Technical risks have mitigations | ✅ | 15% |
| Business rules are explicit | ✅ | 15% |
| Error/edge cases defined | ✅ | 15% |
| UI/UX specs complete | ❌ Skipped (Light mode) | 15% |

**Missing for 100%**:
- Validate playwright-stealth against job sites (OQ-02) — unblocks Phase 3
- UI/UX wireframes (skipped in Light mode; run `/requirements-orchestrator` with Full mode for this feature if needed)

---

## 15. Changelog

| Date | Change |
|------|--------|
| 2026-03-23 | Initial version — Light mode (BA + SA) |
| 2026-03-24 | OQ-01 resolved for Phase 1 with the initial airdrop source list: airdrops.io, CryptoRank, and DeFiLlama |

---

## Next Steps

1. [x] Confirm airdrop target sites (resolve OQ-01)
2. [ ] Test playwright-stealth against TopCV, ITviec, VietnamWorks (resolve OQ-02)
3. [ ] Decide API key UI entry vs .env-only (resolve OQ-03)
4. [ ] Run `/manage-epic` to break into feature plans per phase
5. [ ] Run `/create-plan` to start Phase 1 foundation implementation
