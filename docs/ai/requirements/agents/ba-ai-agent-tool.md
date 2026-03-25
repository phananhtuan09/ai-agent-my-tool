# BA Analysis: AI Agent Tool Web Interface

> Generated: 2026-03-23
> Agent: requirement-ba
> Feature: ai-agent-tool

---

## 1. Problem Statement

### Context
A developer (personal use) needs a unified web interface to manage three independent AI-powered automation tools hosted on a personal VPS. Currently there is no centralized way to trigger, monitor, and interact with these tools.

### Problem
- Job hunting requires manually checking multiple sites (TopCV, ITviec, VietnamWorks) daily — repetitive and time-consuming.
- Daily task scheduling is done manually without AI assistance for time estimation or optimization.
- Tracking crypto airdrops requires monitoring multiple sites frequently — hard to evaluate potential without structured analysis.

### Impact
Without this tool, the developer spends significant manual effort on tasks that can be automated. Each task domain requires separate tooling and context switching.

---

## 2. Target Users

| User Type | Description | Primary Goals |
|-----------|-------------|---------------|
| Developer (personal) | Single user, hosts on VPS, personal productivity | Automate job search, schedule daily work, track airdrops |

---

## 3. User Stories

| ID | Priority | As a... | I want to... | So that... |
|----|----------|---------|--------------|------------|
| US-01 | Must | Developer | Configure job search filters (salary, frameworks, location) | AI only shows me relevant job listings |
| US-02 | Must | Developer | Have jobs crawled daily automatically | I always have fresh listings without manual effort |
| US-03 | Must | Developer | Input my daily tasks and have AI create an optimized schedule | I use my time efficiently |
| US-04 | Must | Developer | Receive hourly reminders to update task progress | I stay on track throughout the day |
| US-05 | Must | Developer | Chat with the scheduler agent to re-schedule remaining tasks | The plan adapts to reality as the day progresses |
| US-06 | Must | Developer | Have airdrop data crawled every 6 hours and AI-analyzed | I see ranked, evaluated airdrops without manual research |
| US-07 | Must | Developer | Chat with the airdrop agent to filter or ask questions | I can drill into specific airdrops interactively |
| US-08 | Must | Developer | Switch LLM provider/model per agent from the UI | I can optimize cost and performance per agent |
| US-09 | Should | Developer | See browser notification when background cron completes | I'm alerted to new results without polling |
| US-10 | Should | Developer | Add new agent tools in the future without touching core code | The system is extensible |

---

## 4. Functional Requirements

### 4.1 Cross-Cutting (All Agents)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-01 | Each agent has its own sidebar navigation entry | Must | Sidebar shows Job Finder, Daily Schedule, Crypto Airdrop |
| FR-02 | Each agent can independently configure LLM provider and model via gear icon modal | Must | Modal shows provider (Anthropic/OpenAI), model name, API key; changes take effect without server restart |
| FR-03 | Each agent has isolated SQLite memory DB | Must | Agents do not share DB; each has its own `memory.db` |
| FR-04 | Agent outputs stream via SSE | Must | Text tokens appear in real-time in chat panel; tool call results update display panel |
| FR-05 | Browser Notification API fires when cron jobs complete (tab must be open) | Must | Notification appears on cron completion; if tab closed, notification is lost (MVP) |
| FR-06 | Agent registry pattern allows adding new agents without modifying core | Should | New agent folder + register() call → appears in sidebar automatically |

### 4.2 Find Job Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-07 | Daily cron crawls TopCV, ITviec, VietnamWorks (configurable sources) | Must | Cron runs daily; results stored in SQLite; each source can be toggled on/off in config |
| FR-08 | Job filter config UI: salary range, must-have frameworks, nice-to-have frameworks, locations, exclude keywords | Must | Config form saves to settings.yaml; hot-reloaded without restart |
| FR-09 | Hard filter first: only jobs matching salary range, location, and must-have keywords pass through | Must | Jobs failing hard criteria are excluded from results |
| FR-10 | AI ranks filtered jobs by relevance and shows match score | Must | Each job card shows AI-generated score (0-100) and reason |
| FR-11 | Job result cards display: title, company, salary, location, tech stack, source, match score, link | Must | All fields visible on card; link opens source in new tab |
| FR-12 | Data retained for 30 days; older records auto-deleted | Must | Records older than 30 days are purged on next crawl |
| FR-13 | Browser notification fires when daily crawl completes | Should | Notification shows count of new matched jobs |
| FR-14 | Crawler failure triggers immediate warning to user | Must | UI shows which source failed; continues with successful sources |

### 4.3 Daily Schedule Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-15 | User inputs tasks via chat in the morning | Must | Chat panel accepts free-text task list; agent parses and confirms |
| FR-16 | Agent estimates time per task and creates optimized schedule | Must | Timeline panel renders ordered task list with start/end times |
| FR-17 | Schedule displays in timeline panel (left); chat panel (right) | Must | Split-panel layout with timeline and chat visible simultaneously |
| FR-18 | Hourly cron (configurable interval) sends reminder message in chat panel | Must | Agent message appears in chat: "X hour passed, update your progress" |
| FR-19 | User replies in chat with progress update; agent re-schedules remaining tasks | Must | Agent parses update, re-renders timeline with remaining tasks from "now" |
| FR-20 | When tasks are overdue, agent asks user interactively what to do | Must | Agent flags overdue tasks in chat and asks user to decide: drop, extend, or defer |
| FR-21 | Today's tasks only stored (Phase 1); data cleared at end of day | Must | Only current day's tasks persist; Phase 2 adds history |

### 4.4 Crypto Airdrop Agent

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-22 | Every 6 hours (configurable), cron crawls airdrop sites | Must | Crawl runs on schedule; results stored in SQLite |
| FR-23 | AI analyzes each airdrop using predefined skill/criteria template | Must | Criteria: team credibility, tokenomics, community size, task difficulty vs reward, chain/ecosystem |
| FR-24 | Airdrop cards displayed ranked by AI potential score | Must | Cards show: name, chain, potential score, requirements summary, deadline, source link |
| FR-25 | User can chat with agent to filter or ask about specific airdrops | Must | Chat panel accepts questions; agent responds and can re-render filtered list |
| FR-26 | Last 10 crawl cycles of data retained; older purged automatically | Must | On each new crawl, oldest cycle deleted if > 10 stored |
| FR-27 | Crawler failure triggers immediate warning; continues with successful sources | Must | Warning shown in UI; partial results still displayed |

---

## 5. Business Rules

| ID | Rule | Condition | Action |
|----|------|-----------|--------|
| BR-01 | Hard filter before AI ranking (Job Agent) | When crawl completes | Apply salary/location/keyword hard filter before sending to LLM |
| BR-02 | Jobs failing hard filter are excluded | When job does not match salary OR location OR must-have keywords | Exclude from results entirely (not shown to user) |
| BR-03 | Crawler failure = warn, not abort | When any source crawler fails | Log error, show warning, continue with other sources |
| BR-04 | Retry policy for crawlers | When crawler fails | Warn user immediately; no retry (keep simple for MVP) |
| BR-05 | Job data purge | When crawl runs | Delete records older than 30 days |
| BR-06 | Airdrop data purge | When new crawl cycle completes | Delete oldest cycle if stored cycles > 10 |
| BR-07 | Schedule only stores today | At end of day (midnight) | Clear all tasks from memory.db |
| BR-08 | Overdue task handling (Schedule) | When task end time has passed and task is not done | Agent flags in chat and asks user to decide interactively |
| BR-09 | Model config applies without restart | When user saves model config in modal | New LLM client initialized immediately; no server restart needed |
| BR-10 | Agent registry auto-discovery | When FastAPI starts | Registry scans agents/ directory and registers all valid agents |
| BR-11 | SSE connection per agent | When user opens an agent page | SSE connection established for that agent's stream |
| BR-12 | Browser notification requires open tab | When cron completes | Notification fires only if tab is open (MVP constraint) |
| BR-13 | Each agent's memory is isolated | At all times | Agents never read/write each other's memory.db |
| BR-14 | Airdrop criteria fixed in skill template (Phase 1) | When evaluating airdrops | Use predefined criteria; user cannot override criteria in Phase 1 |

---

## 6. Out of Scope (MVP)

- Multi-user / authentication
- Service Worker for background push notifications (tab closed)
- Job application tracking or CRM features
- Multi-day task history for Daily Schedule Agent (Phase 2)
- Custom airdrop evaluation criteria via UI (Phase 2)
- Email/Telegram/Slack notification channels
- Mobile-responsive design (VPS personal tool, desktop only)
- Automated job application submission

---

## 7. Open Questions

| ID | Question | Owner | Status | Blocking |
|----|----------|-------|--------|----------|
| OQ-01 | If hourly reminder fires and tab is closed, should missed reminders be queued and shown when user returns? | Developer | Open | No |
| OQ-02 | Which specific airdrop listing sites should be crawled? (airdrops.io? DeFiLlama? CryptoRank?) | Developer | Open | Yes |
| OQ-03 | Should the gear icon modal allow API key entry, or should API keys only be set via .env file? | Developer | Open | No |
| OQ-04 | Should the daily schedule reset automatically at midnight, or should the user manually clear it? | Developer | Open | No |

---

## 8. Domain Glossary

| Term | Definition |
|------|------------|
| SSE | Server-Sent Events: one-way real-time stream from server to browser |
| APScheduler | Python library for scheduling background jobs within a FastAPI process |
| Agent Registry | Pattern where agents self-register on startup; new agents added by creating a folder |
| Hard Filter | Filter that excludes records failing mandatory criteria entirely |
| Soft Filter / AI Rank | AI scores all records by relevance and sorts by score |
| Airdrop | Free token distribution by a crypto project to eligible wallets |
| Crawler | Playwright-based headless browser that extracts data from job/airdrop sites |
| memory.db | Per-agent SQLite database storing agent-specific data and history |
| Skill Template | Predefined prompt template encoding domain-specific evaluation criteria |
| HTMX | JavaScript library for partial HTML updates, used instead of a full SPA framework |

---

## 9. Assumptions

| ID | Assumption |
|----|------------|
| A-01 | User always has browser tab open when using Daily Schedule Agent reminders |
| A-02 | VPS has sufficient memory to run FastAPI + Playwright + APScheduler concurrently |
| A-03 | DuckDuckGo search library provides sufficient results for airdrop research at 6h cadence |
| A-04 | TopCV, ITviec, VietnamWorks do not block Playwright crawlers (rate limiting may apply) |
| A-05 | SQLite write contention between APScheduler and web handlers is acceptable for single-user personal tool |
