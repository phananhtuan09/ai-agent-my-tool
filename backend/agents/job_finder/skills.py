"""Ranking helpers for the Job Finder agent."""

from __future__ import annotations

from backend.agents.job_finder.models import JobRecord
from backend.shared.settings import JobFilterSettings


def build_reason(job: JobRecord, filters: JobFilterSettings) -> str:
    """Generate a deterministic ranking explanation."""

    reasons: list[str] = []
    matched_must = _matched_keywords(job.tech_stack, filters.must_have_frameworks)
    matched_nice = _matched_keywords(job.tech_stack, filters.nice_to_have_frameworks)

    if matched_must:
        reasons.append(f"Matched must-have stack: {', '.join(matched_must)}.")
    if matched_nice:
        reasons.append(f"Nice-to-have overlap: {', '.join(matched_nice)}.")
    if filters.locations and job.location.lower() in {
        location.lower() for location in filters.locations
    }:
        reasons.append(f"Preferred location match: {job.location}.")
    if job.salary_min is not None or job.salary_max is not None:
        reasons.append(f"Salary band: {job.salary_label}.")
    if not reasons:
        reasons.append("Relevant baseline fit from the enabled crawl sources.")

    return " ".join(reasons)


def score_job(job: JobRecord, filters: JobFilterSettings) -> int:
    """Compute a deterministic score when no live LLM ranking is available."""

    score = 42
    matched_must = _matched_keywords(job.tech_stack, filters.must_have_frameworks)
    matched_nice = _matched_keywords(job.tech_stack, filters.nice_to_have_frameworks)

    if filters.salary_min is not None and job.salary_max is not None:
        if job.salary_max >= filters.salary_min:
            score += 14
    if filters.salary_max is not None and job.salary_min is not None:
        if job.salary_min <= filters.salary_max:
            score += 10
    if filters.locations and job.location.lower() in {
        location.lower() for location in filters.locations
    }:
        score += 12
    if filters.must_have_frameworks:
        score += min(len(matched_must) * 11, 22)
    if filters.nice_to_have_frameworks:
        score += min(len(matched_nice) * 5, 10)

    return max(0, min(score, 100))


def _matched_keywords(tech_stack: list[str], keywords: list[str]) -> list[str]:
    lower_stack = {item.lower() for item in tech_stack}
    return [keyword for keyword in keywords if keyword.lower() in lower_stack]
