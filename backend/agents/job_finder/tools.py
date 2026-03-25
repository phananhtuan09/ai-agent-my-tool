"""Crawl, filter, and ranking pipeline for the Job Finder agent."""

from __future__ import annotations

from backend.agents.job_finder.fixtures import get_fixture_jobs
from backend.agents.job_finder.models import JobRecord, JobRunSummary
from backend.agents.job_finder.skills import build_reason, score_job
from backend.exceptions import ConfigError, CrawlError
from backend.shared.crawler import run_serialized
from backend.shared.llm_client import LLMClient
from backend.shared.settings import JobFilterSettings, JobFinderRuntimeSettings


def run_job_pipeline(
    runtime_settings: JobFinderRuntimeSettings,
    llm_client: LLMClient,
    trigger: str,
) -> JobRunSummary:
    """Run crawl, hard filtering, and ranking for one execution."""

    enabled_sources = {
        name: config
        for name, config in runtime_settings.sources.items()
        if config.enabled
    }
    if not enabled_sources:
        raise ConfigError("Enable at least one job source before running a crawl.")

    warnings: list[str] = []

    def crawl_all() -> list[JobRecord]:
        jobs: list[JobRecord] = []
        for source_name, source_config in enabled_sources.items():
            try:
                jobs.extend(_crawl_source(source_name, source_config.simulate_failure))
            except CrawlError as exc:
                warnings.append(str(exc))
        return jobs

    crawled_jobs = run_serialized(crawl_all)
    filtered_jobs = filter_jobs(crawled_jobs, runtime_settings.filters)
    ranked_jobs = rank_jobs(filtered_jobs, llm_client, runtime_settings.filters)

    return JobRunSummary(
        jobs=ranked_jobs,
        warnings=warnings,
        matched_count=len(ranked_jobs),
        filtered_count=len(filtered_jobs),
        crawled_count=len(crawled_jobs),
        trigger=trigger,
    )


def filter_jobs(jobs: list[JobRecord], filters: JobFilterSettings) -> list[JobRecord]:
    """Apply hard filters before ranking."""

    return [job for job in jobs if _passes_hard_filters(job, filters)]


def rank_jobs(
    jobs: list[JobRecord],
    llm_client: LLMClient,
    filters: JobFilterSettings,
) -> list[JobRecord]:
    """Rank jobs with a deterministic fallback that remains usable offline."""

    ranked_jobs: list[JobRecord] = []
    for job in jobs:
        job.ai_score = score_job(job, filters)
        job.ai_reason = build_reason(job, filters)
        if not llm_client.is_configured:
            job.ai_reason = (
                f"{job.ai_reason} Deterministic fallback used because "
                f"{llm_client.api_key_env_var} is not configured."
            )
        ranked_jobs.append(job)

    return sorted(
        ranked_jobs,
        key=lambda item: (item.ai_score or 0, item.salary_max or 0),
        reverse=True,
    )


def _crawl_source(source_name: str, simulate_failure: bool) -> list[JobRecord]:
    if simulate_failure:
        raise CrawlError(f"{source_name} crawl failed; other sources continued.")
    return get_fixture_jobs(source_name)


def _passes_hard_filters(job: JobRecord, filters: JobFilterSettings) -> bool:
    if filters.locations and job.location.lower() not in {
        location.lower() for location in filters.locations
    }:
        return False

    if filters.salary_min is not None and job.salary_max is not None:
        if job.salary_max < filters.salary_min:
            return False
    if filters.salary_max is not None and job.salary_min is not None:
        if job.salary_min > filters.salary_max:
            return False

    lower_stack = {item.lower() for item in job.tech_stack}
    if filters.must_have_frameworks:
        required = {item.lower() for item in filters.must_have_frameworks}
        if not required.issubset(lower_stack):
            return False

    if filters.exclude_keywords:
        combined_tokens = " ".join([job.title, job.company, *job.tech_stack]).lower()
        if any(keyword.lower() in combined_tokens for keyword in filters.exclude_keywords):
            return False

    return True
