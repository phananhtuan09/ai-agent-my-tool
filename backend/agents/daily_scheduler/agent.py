"""Daily Schedule agent runtime and chat workflow."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.agents.base_agent import BaseAgent
from backend.agents.daily_scheduler.models import TaskRecord
from backend.agents.daily_scheduler.repository import DailyScheduleRepository
from backend.agents.daily_scheduler.skills import (
    build_schedule,
    find_overdue_task,
    looks_like_progress_command,
    parse_progress_command,
    parse_task_intake,
    rebuild_remaining_schedule,
    summarize_plan,
)
from backend.exceptions import ConfigError
from backend.shared.events import EventBroker
from backend.shared.settings import AgentSettings, OpenAISettings


PENDING_OVERDUE_TASK_ID = "pending_overdue_task_id"


class DailySchedulerAgent(BaseAgent):
    """Registry-backed daily planning workflow with deterministic scheduling."""

    def __init__(
        self,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
        broker: EventBroker,
    ) -> None:
        super().__init__(
            slug="daily_scheduler",
            title="Daily Schedule",
            summary="Turn free-text task lists into a time-boxed plan with hourly reminders and rescheduling.",
            template_name="daily_scheduler.html",
            accent="teal",
            storage_path=Path(__file__).resolve().parent / "memory.db",
            settings=settings,
            openai_settings=openai_settings,
            broker=broker,
        )
        self.repository = DailyScheduleRepository(self.storage_path)

    def initialize(self) -> None:
        super().initialize()
        self.repository.initialize()

    def register_jobs(self, scheduler: AsyncIOScheduler) -> None:
        runtime = self._get_runtime_settings()
        scheduler.add_job(
            self.send_reminder,
            trigger=CronTrigger.from_crontab(runtime.reminder_cron),
            id=f"{self.slug}-reminder",
            replace_existing=True,
        )
        scheduler.add_job(
            self.reset_day,
            trigger=CronTrigger.from_crontab(runtime.reset_cron),
            id=f"{self.slug}-reset",
            replace_existing=True,
        )

    def build_snapshot(self) -> dict[str, Any]:
        snapshot = super().build_snapshot()
        tasks = self.repository.list_tasks()
        pending_overdue = self._get_pending_overdue_task(tasks)
        if pending_overdue is not None:
            snapshot["status"] = "Awaiting overdue decision"
            snapshot["pending_task"] = pending_overdue.title
            return snapshot

        active_count = sum(task.status in {"pending", "in_progress"} for task in tasks)
        if active_count:
            snapshot["status"] = f"{active_count} tasks scheduled"
        elif tasks:
            snapshot["status"] = "Day completed"
        else:
            snapshot["status"] = "Ready to plan today"
        snapshot["task_count"] = len(tasks)
        return snapshot

    def build_page_context(self) -> dict[str, object]:
        runtime = self._get_runtime_settings()
        tasks = self.repository.list_tasks()
        messages = self.repository.list_messages()
        return {
            "hero_eyebrow": "Adaptive time planning",
            "hero_title": "Daily Schedule Studio",
            "hero_body": "Build a day plan from free-text tasks, keep the timeline live with progress updates, and let reminder/reset jobs reuse the shared SSE channel.",
            "schedule_settings": runtime,
            "schedule_tasks": tasks,
            "schedule_messages": messages,
            "awaiting_overdue_resolution": self._get_pending_overdue_task(tasks) is not None,
        }

    def handle_chat(self, message: str) -> dict[str, object]:
        normalized = message.strip()
        if not normalized:
            raise ConfigError("Send a task list or progress update before submitting.")

        now = datetime.now().astimezone()
        tasks = self.repository.list_tasks()
        pending_overdue = self._get_pending_overdue_task(tasks)
        command = parse_progress_command(normalized)

        self.repository.append_message("user", normalized)
        if pending_overdue is not None:
            reply = self._resolve_overdue(normalized, tasks, pending_overdue, now)
        elif command is not None and command.action == "replace_plan":
            reply = self._create_schedule_from_message(normalized, now)
        elif not tasks:
            if looks_like_progress_command(normalized):
                reply = (
                    "No schedule is active yet. Send a task list first, or use "
                    "`plan: task one, task two` to seed the day."
                )
            else:
                reply = self._create_schedule_from_message(normalized, now)
        elif not looks_like_progress_command(normalized):
            reply = self._create_schedule_from_message(normalized, now)
        else:
            reply = self._apply_progress_update(normalized, tasks, now)

        self.repository.append_message("assistant", reply)
        self.publish("chat", message=reply)
        self.publish("status", snapshot=self.build_snapshot())
        self.publish("ui_update", panel="daily_schedule", data=self._build_ui_payload())
        return {
            "reply": reply,
            "tasks": self.repository.list_tasks(),
            "messages": self.repository.list_messages(),
        }

    def send_reminder(self) -> str | None:
        tasks = self.repository.list_tasks()
        active_tasks = [task for task in tasks if task.status in {"pending", "in_progress"}]
        if not active_tasks:
            return None

        next_task = active_tasks[0]
        message = (
            f"Reminder: {next_task.title} is on deck for {next_task.time_range}. "
            "Reply with `done: ...` or `working on: ...` to refresh the timeline."
        )
        self.repository.append_message("assistant", message)
        self.publish("chat", message=message)
        self.publish("notify", message=message)
        self.publish("status", snapshot=self.build_snapshot())
        self.publish("ui_update", panel="daily_schedule", data=self._build_ui_payload())
        return message

    def reset_day(self) -> None:
        self.repository.clear_day()
        message = "Day reset completed. Start a new plan whenever you're ready."
        self.repository.append_message("assistant", message)
        self.publish("chat", message=message)
        self.publish("notify", message=message)
        self.publish("status", snapshot=self.build_snapshot())
        self.publish("ui_update", panel="daily_schedule", data=self._build_ui_payload())

    def _create_schedule_from_message(self, message: str, now: datetime) -> str:
        runtime = self._get_runtime_settings()
        command = parse_progress_command(message)
        intake_text = command.target if command and command.action == "replace_plan" else message
        drafts = parse_task_intake(intake_text or "", runtime.default_task_minutes)
        if not drafts:
            raise ConfigError(
                "No tasks were detected. Separate tasks with commas, semicolons, or new lines."
            )

        tasks = build_schedule(drafts, runtime, now)
        self.repository.replace_tasks(tasks)
        self.repository.set_state(PENDING_OVERDUE_TASK_ID, None)
        return (
            f"Parsed {len(tasks)} tasks. {summarize_plan(tasks)} "
            "Use `done: task name`, `working on: task name`, `defer: task name`, "
            "or `drop: task name` to keep the schedule current."
        )

    def _apply_progress_update(
        self,
        message: str,
        tasks: list[TaskRecord],
        now: datetime,
    ) -> str:
        command = parse_progress_command(message)
        if command is None or command.action not in {
            "done",
            "working_on",
            "defer_named",
            "drop_named",
        }:
            return (
                "Use `done: task name`, `working on: task name`, `defer: task name`, "
                "`drop: task name`, or `plan: ...` to replace today's schedule."
            )

        task = self._find_task(tasks, command.target)
        if task is None or command.target is None:
            return (
                f"I could not find `{command.target or 'that task'}`. "
                "Try the exact task title from the current timeline."
            )

        if command.action == "done":
            task.status = "done"
        elif command.action == "working_on":
            for candidate in tasks:
                if candidate.id != task.id and candidate.status == "in_progress":
                    candidate.status = "pending"
            task.status = "in_progress"
        elif command.action == "defer_named":
            task.status = "deferred"
        elif command.action == "drop_named":
            task.status = "dropped"

        overdue_task = find_overdue_task(tasks, now)
        if overdue_task is not None:
            self.repository.save_tasks(tasks)
            self.repository.set_state(PENDING_OVERDUE_TASK_ID, str(overdue_task.id))
            return (
                f"`{overdue_task.title}` is overdue. Reply with `keep`, `defer`, or `drop` "
                "so I can reschedule the remaining work from now."
            )

        updated_tasks = rebuild_remaining_schedule(tasks, self._get_runtime_settings(), now)
        self.repository.save_tasks(updated_tasks)
        self.repository.set_state(PENDING_OVERDUE_TASK_ID, None)
        active_count = sum(
            task.status in {"pending", "in_progress"} for task in updated_tasks
        )
        return (
            f"Progress captured. Rescheduled {active_count} remaining task(s) from "
            f"{now.strftime('%H:%M')}."
        )

    def _resolve_overdue(
        self,
        message: str,
        tasks: list[TaskRecord],
        pending_task: TaskRecord,
        now: datetime,
    ) -> str:
        command = parse_progress_command(message)
        if command is None or command.action not in {"keep", "defer", "drop"}:
            return (
                f"Overdue task `{pending_task.title}` still needs a decision. "
                "Reply with `keep`, `defer`, or `drop`."
            )

        if command.action == "keep":
            pending_task.status = "in_progress"
        elif command.action == "defer":
            pending_task.status = "deferred"
        elif command.action == "drop":
            pending_task.status = "dropped"

        updated_tasks = rebuild_remaining_schedule(tasks, self._get_runtime_settings(), now)
        self.repository.save_tasks(updated_tasks)
        self.repository.set_state(PENDING_OVERDUE_TASK_ID, None)
        return (
            f"Recorded `{command.action}` for `{pending_task.title}` and rebuilt the day plan "
            f"from {now.strftime('%H:%M')}."
        )

    def _build_ui_payload(self) -> dict[str, object]:
        tasks = self.repository.list_tasks()
        messages = self.repository.list_messages()
        pending_overdue = self._get_pending_overdue_task(tasks)
        return {
            "tasks": [task.to_event_payload() for task in tasks],
            "messages": [message.to_event_payload() for message in messages],
            "awaiting_overdue_resolution": pending_overdue is not None,
        }

    def _get_pending_overdue_task(self, tasks: list[TaskRecord]) -> TaskRecord | None:
        pending_id = self.repository.get_state(PENDING_OVERDUE_TASK_ID)
        if pending_id is None:
            return None
        for task in tasks:
            if str(task.id) == pending_id:
                return task
        self.repository.set_state(PENDING_OVERDUE_TASK_ID, None)
        return None

    def _find_task(self, tasks: list[TaskRecord], target: str | None) -> TaskRecord | None:
        if not target:
            return None
        normalized_target = target.lower()
        for task in tasks:
            if normalized_target == task.title.lower():
                return task
        for task in tasks:
            if normalized_target in task.title.lower():
                return task
        return None

    def _get_runtime_settings(self):
        if self.settings.daily_scheduler is None:
            raise ConfigError("Daily Scheduler runtime settings are missing.")
        return self.settings.daily_scheduler
