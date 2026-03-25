"""Typed models for the Job Finder agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class JobRecord:
    """Normalized job data stored in SQLite and rendered in the UI."""

    title: str
    company: str
    salary_min: int | None
    salary_max: int | None
    location: str
    tech_stack: list[str]
    source: str
    url: str
    ai_score: int | None = None
    ai_reason: str | None = None
    crawled_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_event_payload(self) -> dict[str, object]:
        """Return a JSON-safe representation for SSE UI updates."""

        return asdict(self)

    @property
    def salary_label(self) -> str:
        if self.salary_min is None and self.salary_max is None:
            return "Negotiable"
        if self.salary_min is None:
            return f"Up to {self.salary_max:,} USD"
        if self.salary_max is None:
            return f"From {self.salary_min:,} USD"
        return f"{self.salary_min:,}-{self.salary_max:,} USD"


@dataclass(slots=True)
class JobRunSummary:
    """Summary of one crawl/filter/rank execution."""

    jobs: list[JobRecord]
    warnings: list[str]
    matched_count: int
    filtered_count: int
    crawled_count: int
    trigger: str
    ran_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
