"""Deterministic parsing and planning helpers for the Daily Scheduler agent."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re

from backend.agents.daily_scheduler.models import TaskRecord
from backend.shared.settings import DailySchedulerRuntimeSettings


COMMAND_PREFIXES = ("done:", "working on:", "defer:", "drop:", "keep", "plan:")
TASK_SPLIT_PATTERN = re.compile(r"[\n;,]+")
DURATION_PATTERN = re.compile(
    r"(?P<value>\d+)\s*(?P<unit>h|hr|hrs|hour|hours|m|min|mins|minute|minutes)\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class TaskDraft:
    """Parsed task draft before schedule times are assigned."""

    title: str
    estimated_minutes: int


@dataclass(slots=True)
class ProgressCommand:
    """Normalized chat command for progress and overdue decisions."""

    action: str
    target: str | None = None


def looks_like_progress_command(message: str) -> bool:
    """Return whether the chat message is an explicit progress command."""

    normalized = message.strip().lower()
    return normalized.startswith(COMMAND_PREFIXES)


def parse_progress_command(message: str) -> ProgressCommand | None:
    """Parse deterministic progress and overdue-decision commands."""

    normalized = message.strip()
    lowered = normalized.lower()

    if lowered in {"keep", "defer", "drop"}:
        return ProgressCommand(action=lowered)

    for prefix, action in (
        ("done:", "done"),
        ("working on:", "working_on"),
        ("defer:", "defer_named"),
        ("drop:", "drop_named"),
        ("plan:", "replace_plan"),
    ):
        if lowered.startswith(prefix):
            target = normalized[len(prefix) :].strip()
            return ProgressCommand(action=action, target=target or None)
    return None


def parse_task_intake(message: str, default_minutes: int) -> list[TaskDraft]:
    """Turn a free-text task list into normalized task drafts."""

    drafts: list[TaskDraft] = []
    for raw_piece in TASK_SPLIT_PATTERN.split(message):
        cleaned = raw_piece.strip(" -\t")
        if not cleaned:
            continue
        duration_match = DURATION_PATTERN.search(cleaned)
        minutes = (
            _duration_to_minutes(duration_match.group("value"), duration_match.group("unit"))
            if duration_match
            else estimate_task_minutes(cleaned, default_minutes)
        )
        title = (
            DURATION_PATTERN.sub("", cleaned)
            .replace("()", "")
            .replace("  ", " ")
            .strip(" -")
        )
        if title:
            drafts.append(TaskDraft(title=title, estimated_minutes=max(15, minutes)))
    return drafts


def build_schedule(
    drafts: list[TaskDraft],
    runtime: DailySchedulerRuntimeSettings,
    now: datetime,
) -> list[TaskRecord]:
    """Assign sequential times for a list of task drafts."""

    cursor = max(now, _workday_anchor(now, runtime.workday_start))
    tasks: list[TaskRecord] = []
    for index, draft in enumerate(drafts):
        start_time = cursor
        end_time = start_time + timedelta(minutes=draft.estimated_minutes)
        tasks.append(
            TaskRecord(
                title=draft.title,
                estimated_minutes=draft.estimated_minutes,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                status="pending",
                sort_order=index,
            )
        )
        cursor = end_time + timedelta(minutes=runtime.focus_break_minutes)
    return tasks


def rebuild_remaining_schedule(
    tasks: list[TaskRecord],
    runtime: DailySchedulerRuntimeSettings,
    now: datetime,
) -> list[TaskRecord]:
    """Reschedule active tasks from the current time while preserving completed work."""

    cursor = now
    rebuilt: list[TaskRecord] = []
    sort_order = 0
    for task in tasks:
        updated = TaskRecord(
            id=task.id,
            title=task.title,
            estimated_minutes=task.estimated_minutes,
            start_time=task.start_time,
            end_time=task.end_time,
            status=task.status,
            sort_order=sort_order,
            created_at=task.created_at,
        )
        if task.status in {"pending", "in_progress"}:
            updated.start_time = cursor.isoformat()
            updated.end_time = (
                cursor + timedelta(minutes=task.estimated_minutes)
            ).isoformat()
            cursor = datetime.fromisoformat(updated.end_time) + timedelta(
                minutes=runtime.focus_break_minutes
            )
        rebuilt.append(updated)
        sort_order += 1
    return rebuilt


def find_overdue_task(tasks: list[TaskRecord], now: datetime) -> TaskRecord | None:
    """Return the first active overdue task, if any."""

    for task in tasks:
        if task.status not in {"pending", "in_progress"}:
            continue
        if datetime.fromisoformat(task.end_time) < now:
            return task
    return None


def estimate_task_minutes(title: str, default_minutes: int) -> int:
    """Estimate task duration from keywords when the user gives no explicit time."""

    lowered = title.lower()
    if any(keyword in lowered for keyword in ("meeting", "standup", "sync")):
        return 30
    if any(keyword in lowered for keyword in ("refactor", "debug", "investigate")):
        return 75
    if any(keyword in lowered for keyword in ("review", "test", "qa")):
        return 45
    if any(keyword in lowered for keyword in ("deploy", "release", "ship")):
        return 30
    if any(keyword in lowered for keyword in ("build", "implement", "feature")):
        return 60
    return default_minutes


def summarize_plan(tasks: list[TaskRecord]) -> str:
    """Create a short confirmation summary for the assistant chat reply."""

    if not tasks:
        return "No schedule was created."
    first = tasks[0]
    last = tasks[-1]
    return (
        f"Planned {len(tasks)} tasks from {first.time_range.split(' - ')[0]} "
        f"to {last.time_range.split(' - ')[1]}."
    )


def _duration_to_minutes(value: str, unit: str) -> int:
    amount = int(value)
    normalized = unit.lower()
    if normalized.startswith("h"):
        return amount * 60
    return amount


def _workday_anchor(now: datetime, workday_start: str) -> datetime:
    hour, minute = [int(part) for part in workday_start.split(":", maxsplit=1)]
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

