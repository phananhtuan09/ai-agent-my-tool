"""Typed models for the Daily Scheduler agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _format_clock(value: str | None) -> str:
    if not value:
        return "--:--"
    return datetime.fromisoformat(value).strftime("%H:%M")


@dataclass(slots=True)
class TaskRecord:
    """Normalized task data stored in SQLite and rendered in the UI."""

    title: str
    estimated_minutes: int
    start_time: str
    end_time: str
    status: str = "pending"
    sort_order: int = 0
    created_at: str = field(default_factory=_now_iso)
    id: int | None = None

    @property
    def time_range(self) -> str:
        return f"{_format_clock(self.start_time)} - {_format_clock(self.end_time)}"

    def to_event_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["time_range"] = self.time_range
        return payload


@dataclass(slots=True)
class ChatMessage:
    """Message row for the schedule chat transcript."""

    role: str
    content: str
    created_at: str = field(default_factory=_now_iso)
    id: int | None = None

    def to_event_payload(self) -> dict[str, object]:
        return asdict(self)

