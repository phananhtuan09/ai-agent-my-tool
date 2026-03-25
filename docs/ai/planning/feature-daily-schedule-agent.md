# Plan: Daily Schedule Agent

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
- `backend/agents/job_finder/agent.py` - Shows the current agent lifecycle pattern for storage initialization, scheduler registration, SSE publication, and page-context building.
- `backend/api/job_finder.py` - Demonstrates how the repository uses HTMX form posts plus partial template responses for agent-specific interactions.

### Reusable Components/Utils
- `backend/shared/settings.py` - Already persists nested agent runtime config and validates cron strings, so the schedule settings should extend the same model instead of creating a parallel config path.
- `backend/shared/events.py` - Already fans out `status`, `notify`, `chat`, and `ui_update` events for live timeline/chat refreshes.
- `frontend/static/app.js` - Existing SSE bootstrap already handles generic `chat` activity and one specialized `ui_update` renderer, making it the right place to add timeline refresh support.

### Architectural Patterns
- `Registry-backed agent runtime`: Keep the scheduler feature behind `BaseAgent` and `AgentRegistry` so the shared shell, sidebar, and config modal stay unchanged.
- `Server-rendered interaction loop`: Prefer HTMX partial responses and SSE event payloads over client-side state management.

### Key Files to Reference
- `docs/ai/requirements/req-ai-agent-tool.md` - Source of FR-15 through FR-21, BR-07 through BR-09, and the scheduler acceptance scenarios.
- `docs/ai/requirements/agents/sa-ai-agent-tool.md` - Defines the `tasks` table, reminder/reset cron behavior, and SSE delivery expectations for the scheduling slice.
- `frontend/templates/daily_scheduler.html` - Existing split-panel shell that the real timeline and chat experience must preserve.

---

## 3. Goal & Acceptance Criteria

### Goal
- Replace the Daily Schedule placeholder with a real agent that can parse free-text task intake, estimate durations with a deterministic fallback planner, render a timeline, send hourly reminders, and reschedule remaining work from chat updates without changing the shared shell.

### Acceptance Criteria (Given/When/Then)
- Given the user opens the Daily Schedule page, when the page renders, then it shows a split layout with a schedule settings form, a timeline panel, a chat form, and the latest timeline rows from SQLite.
- Given the user sends a free-text morning task list, when the agent processes the message, then it confirms the parsed tasks in chat and renders an ordered schedule with start/end times.
- Given a reminder cron fires while today tasks exist, when the scheduler job runs, then the chat feed receives a reminder message without a manual page refresh.
- Given the user sends a progress update after work has shifted, when the agent handles the update, then it reschedules remaining tasks from the current time and re-renders the timeline.
- Given one planned task is already overdue, when the user sends a progress update, then the agent asks what to do with the overdue task before rebuilding the rest of the schedule.
- Given the midnight reset job runs, when it clears the day, then persisted schedule rows are removed and the page returns to an empty-state timeline.

## 4. Risks & Assumptions

### Risks
- The shared `LLMClient` is only a descriptor today, so schedule estimation and task parsing need a deterministic fallback that still leaves a clean path to a real LLM implementation later.
- Overdue handling can easily become ambiguous if the chat grammar is too loose, so the first pass needs explicit command patterns for progress and overdue decisions.
- Scheduler jobs and manual chat updates both touch the same SQLite file, so repository writes must remain simple and transactional.

### Assumptions
- A deterministic planner is acceptable for this slice as long as the UI and storage contracts are compatible with a later LLM-backed implementation.
- Progress updates can use concise chat commands such as `done: task name`, `working on: task name`, `defer: task name`, and `drop: task name`.
- A single reminder cron plus a midnight reset cron are sufficient to satisfy the MVP schedule lifecycle.

### Concrete Settings Shape

```yaml
agents:
  daily_scheduler:
    provider: openai
    model: gpt-5-mini
    api_key_env_var: OPENAI_API_KEY
    daily_scheduler:
      reminder_cron: "0 * * * *"
      reset_cron: "0 0 * * *"
      workday_start: "09:00"
      focus_break_minutes: 10
      default_task_minutes: 45
```

The nested `daily_scheduler` payload should round-trip through `save_agent_settings("daily_scheduler", {"daily_scheduler": ...})` and reuse the same cron validation pattern already used by the Job Finder slice.

## 5. Definition of Done
- [x] Build passes (linter, type checks, compile)
- [x] Tests added and passing
- [ ] Code reviewed and approved
- [x] Documentation updated

---

## 6. Implementation Plan

### Summary
Implement the Daily Schedule slice in three passes: add typed runtime settings plus SQLite-backed task storage first, wire the deterministic planner and chat/reschedule flow second, then finish the split-panel UI, SSE updates, and focused validation. Keep the scheduling grammar explicit so the feature remains reliable without a real LLM backend.

### Phase 1: Scheduler Settings And Persistence

- [x] [MODIFIED] `backend/shared/settings.py`, `config/settings.yaml` - Extend the settings document to support nested Daily Schedule runtime config.
  ```text
  Function: load_settings() / save_agent_settings(agent_name, payload)

  Input validation:
    - reminder_cron, reset_cron: valid 5-field crontab strings
    - workday_start: "HH:MM" 24-hour format
    - focus_break_minutes: integer >= 0
    - default_task_minutes: integer >= 15

  Logic flow:
    1. Add typed nested models for the daily schedule runtime section.
    2. Preserve compatibility for other agents by keeping the new nested config optional.
    3. Persist validated nested scheduler settings back to YAML without losing sibling agent sections.
    4. Reject invalid cron/time values without mutating the active file contents.

  Return: validated AppSettings | Error(ConfigError)

  Edge cases:
    - malformed YAML -> keep the file untouched and surface ConfigError
    - invalid HH:MM value -> reject with validation feedback
    - missing nested config in existing documents -> fall back to defaults only where explicitly allowed

  Dependencies: pydantic, PyYAML, filelock, APScheduler CronTrigger
  ```

- [x] [ADDED] `backend/agents/daily_scheduler/models.py`, `backend/agents/daily_scheduler/repository.py`, `backend/agents/daily_scheduler/skills.py` - Add typed task/message models, SQLite helpers, and deterministic scheduling heuristics.
  ```text
  Function: initialize() / replace_tasks(tasks) / list_tasks() / append_message(role, content) / plan_schedule(task_text, runtime, now)

  Input validation:
    - task title: trimmed non-empty string
    - estimated_minutes: integer >= 15
    - status: one of "pending" | "in_progress" | "done" | "deferred" | "dropped"
    - free-text intake: at least one parseable task item

  Logic flow:
    1. Create `tasks` and `messages` tables with today-oriented timestamps.
    2. Parse free-text task input into normalized task drafts with deterministic duration estimates.
    3. Generate ordered start/end times beginning at the configured workday start or `now`, whichever is later.
    4. Store the resulting tasks and assistant/user messages transactionally.
    5. Provide repository helpers for list, clear, and status updates used by chat and cron flows.

  Return: planned task rows and chat message rows | Error(ConfigError, sqlite3.DatabaseError)

  Edge cases:
    - no parseable tasks -> reject with user-facing validation
    - explicit duration missing -> use the configured default duration
    - all tasks cleared -> return an empty-state timeline

  Dependencies: sqlite3, datetime, re
  ```

### Phase 2: Chat Workflow, Rescheduling, And Cron Hooks

- [x] [MODIFIED] `backend/agents/daily_scheduler/agent.py`, `backend/agents/base_agent.py`, `backend/main.py` - Replace the placeholder with a stateful scheduler agent that owns reminders, reset jobs, and live timeline updates.
  ```text
  Function: DailySchedulerAgent.initialize() / register_jobs(scheduler) / handle_chat(message) / send_reminder() / reset_day()

  Input validation:
    - chat message: trimmed non-empty string
    - progress commands: support deterministic prefixes for done / working on / defer / drop / keep
    - overdue resolution: only accepted when the agent has a pending overdue decision

  Logic flow:
    1. Initialize the repository schema and load any persisted today state on startup.
    2. Register reminder and reset scheduler jobs from the validated runtime config.
    3. Treat the first task-intake message as plan creation; later messages as progress or overdue-decision messages.
    4. When a progress update arrives, update task statuses, detect overdue tasks, and either ask for a decision or rebuild remaining start/end times from `now`.
    5. Publish `chat`, `status`, and `ui_update` events after every meaningful state change.
    6. Clear tasks/messages and publish a reset notice when the midnight job fires.

  Return: interaction summary plus latest task/message state | Error(ConfigError)

  Edge cases:
    - reminder fires with no tasks -> do nothing
    - overdue task exists -> hold reschedule until the user replies with a supported decision
    - user references an unknown task title -> return a chat clarification message without mutating other tasks

  Dependencies: APScheduler, repository helpers, shared events
  ```

- [x] [ADDED] `backend/api/daily_scheduler.py`, `frontend/templates/partials/daily_scheduler_controls.html`, `frontend/templates/partials/daily_schedule_timeline.html`, `frontend/templates/partials/daily_schedule_chat.html` - Add HTMX endpoints and partials for scheduler settings, chat submission, and timeline refresh.
  ```text
  Function: GET /agents/daily_scheduler/controls / POST /agents/daily_scheduler/settings / POST /agents/daily_scheduler/chat

  Input validation:
    - settings form values normalized from strings
    - chat submissions reject blank messages
    - schedule settings persist only valid runtime config

  Logic flow:
    1. Render the scheduler controls partial with the saved runtime values.
    2. Save reminder/reset/workday settings and re-register scheduler jobs.
    3. Submit chat messages through the agent workflow and return refreshed timeline/chat partials.
    4. Reuse repository-backed task/message state for every response instead of transient in-memory views.

  Return: HTML partials | Error(HTTP 400, HTTP 422, HTTP 500)

  Edge cases:
    - malformed YAML before save -> return inline error and preserve current UI state
    - blank message -> 422 feedback without altering the timeline
    - reset already cleared the day -> render empty state plus follow-up guidance

  Dependencies: FastAPI form handling, DailySchedulerAgent, shared settings
  ```

### Phase 3: Split-Panel UI, SSE Rendering, And Validation

- [x] [MODIFIED] `frontend/templates/daily_scheduler.html`, `frontend/static/app.js`, `frontend/static/style.css` - Replace the placeholder lane copy with the real split-panel controls, chat stream, timeline state, and SSE timeline renderer.
  ```text
  Function: daily scheduler page render / renderScheduleTimeline(payload)

  Input validation:
    - template context includes scheduler settings, tasks, and message history
    - SSE timeline payload only contains JSON-safe task/message fields

  Logic flow:
    1. Render the settings form and chat composer in the right panel.
    2. Render timeline rows in the left panel with status badges and time ranges.
    3. Extend app.js to refresh the schedule timeline and chat transcript when the agent publishes `ui_update`.
    4. Preserve the existing generic activity feed for high-level event logging and notifications.

  Return: updated UI shell and client-side live-refresh behavior

  Edge cases:
    - no tasks yet -> meaningful empty state
    - overdue resolution pending -> prominent guidance in chat feedback
    - browser notifications denied -> in-page chat/timeline updates still work

  Dependencies: HTMX, Notification API, existing app shell
  ```

- [x] [MODIFIED] `tests/test_app.py` - Add focused coverage for morning intake, progress-driven rescheduling, overdue branching, reminder/reset side effects, and scheduler settings validation.
  ```text
  Function: TestClient coverage for Daily Schedule routes and agent workflow

  Input validation:
    - test payloads must use valid cron strings and supported command prefixes
    - deterministic planner assertions should pin task ordering and status transitions

  Logic flow:
    1. Verify the Daily Schedule page renders controls, chat, and empty timeline states.
    2. Verify free-text intake creates persisted tasks and renders ordered time ranges.
    3. Verify progress updates reschedule remaining tasks from now.
    4. Verify overdue tasks produce a decision prompt before rescheduling.
    5. Verify reminder and reset jobs publish/persist the expected state transitions.

  Return: passing coverage for the scheduling slice

  Edge cases:
    - blank chat submission -> inline validation error
    - unknown task command -> clarification message with no destructive mutation
    - midnight reset after a populated day -> empty timeline and reset chat entry

  Dependencies: FastAPI TestClient
  ```

## 7. Follow-ups
- [ ] Replace deterministic parsing and duration estimation with structured LLM planning once the shared LLM client supports real completions.
- [ ] Add finer-grained progress syntax such as percentage updates or partial task completion when the chat workflow proves stable.
- [ ] Add integration tests around APScheduler timing and SSE delivery once the environment includes pytest and the optional runtime dependencies.
