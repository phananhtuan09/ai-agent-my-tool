"""Foundation placeholder for the Job Finder agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.agents.base_agent import BaseAgent
from backend.agents.job_finder.models import JobRunSummary
from backend.agents.job_finder.repository import JobRepository
from backend.agents.job_finder.tools import run_job_pipeline
from backend.exceptions import ConfigError
from backend.shared.events import EventBroker
from backend.shared.settings import AgentSettings


class JobFinderAgent(BaseAgent):
    """Registry-backed metadata for the job finder workflow."""

    def __init__(self, settings: AgentSettings, broker: EventBroker) -> None:
        super().__init__(
            slug="job_finder",
            title="Job Finder",
            summary="Track relevant Vietnam-based job opportunities with a hard-filter-first workflow.",
            template_name="job_finder.html",
            accent="copper",
            storage_path=Path(__file__).resolve().parent / "memory.db",
            settings=settings,
            broker=broker,
        )
        self.repository = JobRepository(self.storage_path)
        self.is_processing = False
        self.last_run_summary: JobRunSummary | None = None

    def initialize(self) -> None:
        super().initialize()
        self.repository.initialize()

    def register_jobs(self, scheduler: AsyncIOScheduler) -> None:
        runtime = self._get_runtime_settings()
        scheduler.add_job(
            self.run_scheduled_crawl,
            trigger=CronTrigger.from_crontab(runtime.cron),
            id=f"{self.slug}-daily-crawl",
            replace_existing=True,
        )

    def run_scheduled_crawl(self) -> JobRunSummary:
        return self.run_crawl(trigger="scheduled")

    def run_crawl(self, trigger: str = "manual") -> JobRunSummary:
        if self.is_processing:
            raise ConfigError("Job Finder crawl already in progress.")

        runtime = self._get_runtime_settings()
        self.is_processing = True
        try:
            summary = run_job_pipeline(runtime, self.llm_client, trigger=trigger)
            self.repository.purge_old_jobs()
            self.repository.upsert_ranked_jobs(summary.jobs)
            summary.jobs = self.repository.list_ranked_jobs()
            self.last_run_summary = summary
            self.publish(
                "notify",
                message=(
                    f"Job Finder crawl finished with {summary.matched_count} matched jobs "
                    f"from {summary.crawled_count} crawled listings."
                ),
            )
            self.publish("status", snapshot=self.build_snapshot())
            self.publish(
                "ui_update",
                panel="job_results",
                data=[job.to_event_payload() for job in summary.jobs],
                warnings=summary.warnings,
                matched_count=summary.matched_count,
                trigger=summary.trigger,
            )
            for warning in summary.warnings:
                self.publish("notify", message=warning)
            return summary
        finally:
            self.is_processing = False

    def build_snapshot(self) -> dict[str, Any]:
        snapshot = super().build_snapshot()
        if self.is_processing:
            snapshot["status"] = "Crawl in progress"
        elif self.last_run_summary is not None:
            snapshot["status"] = (
                f"{self.last_run_summary.matched_count} matches ready"
                if self.last_run_summary.matched_count
                else "No matches yet"
            )
            snapshot["matched_count"] = self.last_run_summary.matched_count
            snapshot["warning_count"] = len(self.last_run_summary.warnings)
        return snapshot

    def build_page_context(self) -> dict[str, object]:
        runtime = self._get_runtime_settings()
        jobs = self.repository.list_ranked_jobs()
        summary = self.last_run_summary
        return {
            "hero_eyebrow": "Daily crawl runway",
            "hero_title": "Job Finder Console",
            "hero_body": "Crawl configured sources, hard-filter listings before ranking, and keep the latest ranked matches visible from SQLite-backed storage.",
            "job_settings": runtime,
            "jobs": jobs,
            "job_summary": summary,
            "job_warnings": summary.warnings if summary else [],
            "activity_title": "Live agent activity",
            "activity_items": [
                "Save filters to update settings.yaml without a restart.",
                "Run Crawl stores ranked jobs and pushes a completion notification.",
            ],
            "insight_cards": [
                {
                    "title": "Hard filter first",
                    "body": "Salary, location, must-have stack, and exclude keywords are applied before ranking.",
                },
                {
                    "title": "Retention rule",
                    "body": "Rows older than 30 days are purged before storing the latest crawl results.",
                },
            ],
        }

    def _get_runtime_settings(self):
        if self.settings.job_finder is None:
            raise ConfigError("Job Finder runtime settings are missing.")
        return self.settings.job_finder
