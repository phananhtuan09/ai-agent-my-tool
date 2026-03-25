"""Typed models for the Crypto Airdrop agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class AirdropRecord:
    """Normalized airdrop data stored in SQLite and rendered in the UI."""

    name: str
    chain: str
    requirements_summary: str
    source: str
    source_url: str
    deadline: str | None
    team_signal: str
    tokenomics_signal: str
    community_signal: str
    task_reward_signal: str
    ai_score: int | None = None
    ai_reason: str | None = None
    crawl_cycle_id: int | None = None
    crawled_at: str = field(default_factory=_now_iso)

    def to_event_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class AirdropRunSummary:
    """Summary of one crawl and ranking execution."""

    airdrops: list[AirdropRecord]
    warnings: list[str]
    matched_count: int
    crawled_count: int
    trigger: str
    crawl_cycle_id: int | None = None
    ran_at: str = field(default_factory=_now_iso)


@dataclass(slots=True)
class AirdropChatMessage:
    """Stored chat transcript rows for filter interactions."""

    role: str
    content: str
    created_at: str = field(default_factory=_now_iso)
    id: int | None = None

    def to_event_payload(self) -> dict[str, object]:
        return asdict(self)

