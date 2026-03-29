"""Base contract for registry-driven agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sqlite3

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.shared.events import EventBroker
from backend.shared.llm_client import LLMClient
from backend.shared.settings import AgentSettings, OpenAISettings, resolve_agent_storage_path


class BaseAgent:
    """Common metadata and infrastructure helpers shared by all agents."""

    def __init__(
        self,
        *,
        slug: str,
        title: str,
        summary: str,
        template_name: str,
        accent: str,
        storage_path: Path,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
        broker: EventBroker,
    ) -> None:
        self.slug = slug
        self.title = title
        self.summary = summary
        self.template_name = template_name
        self.accent = accent
        self.storage_path = resolve_agent_storage_path(storage_path, slug)
        self.settings = settings
        self.openai_settings = openai_settings
        self.broker = broker
        self.llm_client = LLMClient.from_settings(settings, openai_settings)

    def initialize(self) -> None:
        """Prepare per-agent storage and broker registration."""

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("PRAGMA journal_mode=WAL;")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO agent_meta(key, value)
                VALUES ('title', ?), ('provider', ?), ('model', ?)
                """,
                (self.title, "openai", self.llm_client.model),
            )
            connection.commit()

        self.broker.register_agent(self.slug)

    def reload_settings(
        self,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
    ) -> None:
        """Hot-swap the agent settings after settings.yaml changes."""

        self.settings = settings
        self.openai_settings = openai_settings
        self.llm_client = LLMClient.from_settings(settings, openai_settings)

    def reload_llm_client(
        self,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
    ) -> None:
        """Backward-compatible wrapper around the generic settings reload."""

        self.reload_settings(settings, openai_settings)

    def build_snapshot(self) -> dict[str, Any]:
        """Return the current status snapshot used by dashboard and SSE."""

        summary = self.llm_client.to_summary()
        return {
            "agent_name": self.slug,
            "title": self.title,
            "summary": self.summary,
            "accent": self.accent,
            "provider": summary["provider"],
            "base_url": summary["base_url"],
            "model": summary["model"],
            "model_source": summary["model_source"],
            "is_configured": summary["is_configured"],
            "storage_path": str(self.storage_path),
            "status": (
                "Configured"
                if summary["is_configured"]
                else "Needs OpenAI API key"
            ),
        }

    def publish(self, event_type: str, **payload: Any) -> None:
        """Send an event to current SSE subscribers."""

        event = {"type": event_type, **payload}
        self.broker.publish(self.slug, event)

    def register_jobs(self, scheduler: AsyncIOScheduler) -> None:
        """Allow later feature plans to register cron jobs."""

    def build_page_context(self) -> dict[str, Any]:
        """Return UI-specific context for the agent page."""

        return {
            "hero_eyebrow": "Foundation slice",
            "hero_title": self.title,
            "hero_body": self.summary,
            "workspace_title": "Workspace",
            "workspace_items": [],
            "activity_title": "Activity feed",
            "activity_items": [],
            "insight_cards": [],
        }
