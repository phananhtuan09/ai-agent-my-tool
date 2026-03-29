"""Crypto Airdrop agent runtime, crawl pipeline, and chat filters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.agents.base_agent import BaseAgent
from backend.agents.crypto_airdrop.models import AirdropRecord, AirdropRunSummary
from backend.agents.crypto_airdrop.repository import CryptoAirdropRepository
from backend.agents.crypto_airdrop.tools import apply_chat_filter, run_airdrop_pipeline
from backend.exceptions import ConfigError
from backend.shared.events import EventBroker
from backend.shared.settings import AgentSettings, OpenAISettings


class CryptoAirdropAgent(BaseAgent):
    """Registry-backed crypto airdrop workflow with ranked results and chat filters."""

    def __init__(
        self,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
        broker: EventBroker,
    ) -> None:
        super().__init__(
            slug="crypto_airdrop",
            title="Crypto Airdrop",
            summary="Monitor promising airdrops with scheduled crawling, AI scoring, and interactive filtering.",
            template_name="crypto_airdrop.html",
            accent="amber",
            storage_path=Path(__file__).resolve().parent / "memory.db",
            settings=settings,
            openai_settings=openai_settings,
            broker=broker,
        )
        self.repository = CryptoAirdropRepository(self.storage_path)
        self.is_processing = False
        self.last_run_summary: AirdropRunSummary | None = None
        self.last_filtered_airdrops: list[AirdropRecord] | None = None

    def initialize(self) -> None:
        super().initialize()
        self.repository.initialize()
        self.last_filtered_airdrops = None

    def register_jobs(self, scheduler: AsyncIOScheduler) -> None:
        runtime = self._get_runtime_settings()
        scheduler.add_job(
            self.run_scheduled_crawl,
            trigger=CronTrigger.from_crontab(runtime.cron),
            id=f"{self.slug}-crawl",
            replace_existing=True,
        )

    def run_scheduled_crawl(self) -> AirdropRunSummary:
        return self.run_crawl(trigger="scheduled")

    def run_crawl(self, trigger: str = "manual") -> AirdropRunSummary:
        if self.is_processing:
            raise ConfigError("Crypto Airdrop crawl already in progress.")

        runtime = self._get_runtime_settings()
        self.is_processing = True
        try:
            summary = run_airdrop_pipeline(runtime, self.llm_client, trigger=trigger)
            cycle_id = self.repository.start_cycle()
            for airdrop in summary.airdrops:
                airdrop.crawl_cycle_id = cycle_id
            self.repository.replace_cycle_airdrops(cycle_id, summary.airdrops)
            self.repository.complete_cycle(cycle_id)
            self.repository.purge_old_cycles()
            summary.crawl_cycle_id = cycle_id
            summary.airdrops = self.repository.list_latest_airdrops()
            self.last_run_summary = summary
            self.last_filtered_airdrops = summary.airdrops
            self.publish(
                "notify",
                message=(
                    f"Crypto Airdrop crawl finished with {summary.matched_count} ranked "
                    f"airdrops from {summary.crawled_count} crawled records."
                ),
            )
            for warning in summary.warnings:
                self.publish("notify", message=warning)
            self.publish("status", snapshot=self.build_snapshot())
            self.publish("ui_update", panel="airdrop_results", data=self._build_ui_payload())
            return summary
        finally:
            self.is_processing = False

    def handle_chat(self, message: str) -> dict[str, object]:
        normalized = message.strip()
        if not normalized:
            raise ConfigError("Send a filter request or question before submitting.")

        current_airdrops = self.repository.list_latest_airdrops()
        self.repository.append_message("user", normalized)
        filtered_airdrops, reply = apply_chat_filter(current_airdrops, normalized)
        self.repository.append_message("assistant", reply)
        self.last_filtered_airdrops = filtered_airdrops
        self.publish("chat", message=reply)
        self.publish("status", snapshot=self.build_snapshot())
        self.publish("ui_update", panel="airdrop_results", data=self._build_ui_payload())
        return {
            "reply": reply,
            "airdrops": filtered_airdrops,
            "messages": self.repository.list_messages(),
        }

    def build_snapshot(self) -> dict[str, Any]:
        snapshot = super().build_snapshot()
        if self.is_processing:
            snapshot["status"] = "Crawl in progress"
            return snapshot
        records = self.repository.list_latest_airdrops()
        if records:
            snapshot["status"] = f"{len(records)} ranked opportunities"
            snapshot["matched_count"] = len(records)
        else:
            snapshot["status"] = "No ranked opportunities yet"
        if self.last_run_summary is not None:
            snapshot["warning_count"] = len(self.last_run_summary.warnings)
        return snapshot

    def build_page_context(self) -> dict[str, object]:
        runtime = self._get_runtime_settings()
        airdrops = self.repository.list_latest_airdrops()
        messages = self.repository.list_messages()
        return {
            "hero_eyebrow": "Opportunity radar",
            "hero_title": "Crypto Airdrop Desk",
            "hero_body": "Crawl the configured sources, rank the latest opportunities with a deterministic rubric, and filter the current cycle from chat without leaving the page.",
            "airdrop_settings": runtime,
            "airdrops": airdrops,
            "filtered_airdrops": airdrops if self.last_filtered_airdrops is None else self.last_filtered_airdrops,
            "airdrop_summary": self.last_run_summary,
            "airdrop_warnings": self.last_run_summary.warnings if self.last_run_summary else [],
            "airdrop_messages": messages,
        }

    def _build_ui_payload(self) -> dict[str, object]:
        airdrops = (
            self.repository.list_latest_airdrops()
            if self.last_filtered_airdrops is None
            else self.last_filtered_airdrops
        )
        summary = self.last_run_summary
        return {
            "airdrops": [airdrop.to_event_payload() for airdrop in airdrops],
            "messages": [message.to_event_payload() for message in self.repository.list_messages()],
            "warnings": summary.warnings if summary else [],
            "matched_count": len(airdrops),
            "trigger": summary.trigger if summary else "chat",
        }

    def _get_runtime_settings(self):
        if self.settings.crypto_airdrop is None:
            raise ConfigError("Crypto Airdrop runtime settings are missing.")
        return self.settings.crypto_airdrop
