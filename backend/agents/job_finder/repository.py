"""SQLite persistence for Job Finder records."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sqlite3

from backend.agents.job_finder.models import JobRecord


class JobRepository:
    """Encapsulates SQLite reads and writes for job data."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path

    def initialize(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    location TEXT NOT NULL,
                    tech_stack TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT NOT NULL,
                    ai_score INTEGER,
                    ai_reason TEXT,
                    crawled_at TEXT NOT NULL,
                    UNIQUE(source, url)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(ai_score DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_crawled ON jobs(crawled_at DESC)"
            )
            connection.commit()

    def purge_old_jobs(self) -> None:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM jobs WHERE crawled_at < ?", (cutoff,))
            connection.commit()

    def upsert_ranked_jobs(self, jobs: list[JobRecord]) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM jobs")
            connection.executemany(
                """
                INSERT INTO jobs(
                    title, company, salary_min, salary_max, location, tech_stack,
                    source, url, ai_score, ai_reason, crawled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, url) DO UPDATE SET
                    title = excluded.title,
                    company = excluded.company,
                    salary_min = excluded.salary_min,
                    salary_max = excluded.salary_max,
                    location = excluded.location,
                    tech_stack = excluded.tech_stack,
                    ai_score = excluded.ai_score,
                    ai_reason = excluded.ai_reason,
                    crawled_at = excluded.crawled_at
                """,
                [
                    (
                        job.title,
                        job.company,
                        job.salary_min,
                        job.salary_max,
                        job.location,
                        json.dumps(job.tech_stack),
                        job.source,
                        job.url,
                        job.ai_score,
                        job.ai_reason,
                        job.crawled_at,
                    )
                    for job in jobs
                ],
            )
            connection.commit()

    def list_ranked_jobs(self, limit: int = 24) -> list[JobRecord]:
        with sqlite3.connect(self.storage_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT title, company, salary_min, salary_max, location, tech_stack,
                       source, url, ai_score, ai_reason, crawled_at
                FROM jobs
                ORDER BY ai_score DESC, crawled_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            JobRecord(
                title=row["title"],
                company=row["company"],
                salary_min=row["salary_min"],
                salary_max=row["salary_max"],
                location=row["location"],
                tech_stack=json.loads(row["tech_stack"]),
                source=row["source"],
                url=row["url"],
                ai_score=row["ai_score"],
                ai_reason=row["ai_reason"],
                crawled_at=row["crawled_at"],
            )
            for row in rows
        ]
