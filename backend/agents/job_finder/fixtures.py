"""Deterministic fixture data for the Job Finder agent."""

from __future__ import annotations

from backend.agents.job_finder.models import JobRecord


_FIXTURE_JOBS: dict[str, list[JobRecord]] = {
    "topcv": [
        JobRecord(
            title="Senior React Engineer",
            company="Saigon Product Studio",
            salary_min=1800,
            salary_max=2600,
            location="Ho Chi Minh City",
            tech_stack=["React", "TypeScript", "Next.js"],
            source="topcv",
            url="https://topcv.vn/jobs/senior-react-engineer",
        ),
        JobRecord(
            title="Backend Python Developer",
            company="Delta Logistics",
            salary_min=1400,
            salary_max=2100,
            location="Da Nang",
            tech_stack=["Python", "FastAPI", "PostgreSQL"],
            source="topcv",
            url="https://topcv.vn/jobs/backend-python-developer",
        ),
    ],
    "itviec": [
        JobRecord(
            title="Fullstack JavaScript Engineer",
            company="Lotus Commerce",
            salary_min=1600,
            salary_max=2400,
            location="Ho Chi Minh City",
            tech_stack=["React", "Node.js", "TypeScript"],
            source="itviec",
            url="https://itviec.com/jobs/fullstack-javascript-engineer",
        ),
        JobRecord(
            title="Frontend Vue Developer",
            company="Hue Digital Works",
            salary_min=1200,
            salary_max=1700,
            location="Remote",
            tech_stack=["Vue", "Nuxt", "Tailwind"],
            source="itviec",
            url="https://itviec.com/jobs/frontend-vue-developer",
        ),
    ],
    "vietnamworks": [
        JobRecord(
            title="Lead Frontend Platform Engineer",
            company="Northstar Fintech",
            salary_min=2200,
            salary_max=3200,
            location="Hanoi",
            tech_stack=["React", "TypeScript", "Design Systems"],
            source="vietnamworks",
            url="https://www.vietnamworks.com/lead-frontend-platform-engineer",
        ),
        JobRecord(
            title="Mobile Engineer",
            company="Mekong Mobility",
            salary_min=1500,
            salary_max=2200,
            location="Ho Chi Minh City",
            tech_stack=["Flutter", "Dart", "Firebase"],
            source="vietnamworks",
            url="https://www.vietnamworks.com/mobile-engineer",
        ),
    ],
}


def get_fixture_jobs(source: str) -> list[JobRecord]:
    """Return a copy of the deterministic fixture data for one source."""

    jobs = _FIXTURE_JOBS.get(source, [])
    return [
        JobRecord(
            title=job.title,
            company=job.company,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            location=job.location,
            tech_stack=list(job.tech_stack),
            source=job.source,
            url=job.url,
        )
        for job in jobs
    ]
