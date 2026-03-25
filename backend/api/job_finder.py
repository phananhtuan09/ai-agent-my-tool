"""HTMX endpoints for the Job Finder agent."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from backend.agents.job_finder.agent import JobFinderAgent
from backend.exceptions import AgentError, ConfigError
from backend.shared.settings import save_agent_settings


router = APIRouter()


def _get_templates(request: Request):
    return request.app.state.templates


def _resolve_agent(request: Request) -> JobFinderAgent:
    registry = request.app.state.registry
    try:
        agent = registry.get("job_finder")
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return agent


@router.get("/agents/job_finder/filters", response_class=HTMLResponse)
async def get_job_filters(request: Request) -> HTMLResponse:
    """Render the Job Finder filter form partial."""

    agent = _resolve_agent(request)
    context = {
        "request": request,
        "current_agent": agent,
        "job_settings": agent._get_runtime_settings(),
        "filter_feedback": None,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/job_finder_filters.html",
        context,
    )


@router.post("/agents/job_finder/filters", response_class=HTMLResponse)
async def save_job_filters(
    request: Request,
    salary_min: str = Form(""),
    salary_max: str = Form(""),
    locations: str = Form(""),
    must_have_frameworks: str = Form(""),
    nice_to_have_frameworks: str = Form(""),
    exclude_keywords: str = Form(""),
    cron: str = Form(...),
    topcv_enabled: str | None = Form(default=None),
    itviec_enabled: str | None = Form(default=None),
    vietnamworks_enabled: str | None = Form(default=None),
) -> HTMLResponse:
    """Persist nested Job Finder runtime settings."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)

    payload = {
        "job_finder": {
            "cron": cron.strip(),
            "sources": {
                "topcv": {
                    "enabled": topcv_enabled == "on",
                    "label": "TopCV",
                },
                "itviec": {
                    "enabled": itviec_enabled == "on",
                    "label": "ITviec",
                },
                "vietnamworks": {
                    "enabled": vietnamworks_enabled == "on",
                    "label": "VietnamWorks",
                },
            },
            "filters": {
                "salary_min": _normalize_int(salary_min),
                "salary_max": _normalize_int(salary_max),
                "locations": _split_csv(locations),
                "must_have_frameworks": _split_csv(must_have_frameworks),
                "nice_to_have_frameworks": _split_csv(nice_to_have_frameworks),
                "exclude_keywords": _split_csv(exclude_keywords),
            },
        }
    }

    try:
        settings = save_agent_settings("job_finder", payload)
        updated_settings = settings.agents["job_finder"]
        agent.reload_settings(updated_settings)
        agent.register_jobs(request.app.state.scheduler)
        filter_feedback = {
            "message_type": "success",
            "message": "Job filter settings saved and reloaded.",
        }
        status_code = status.HTTP_200_OK
        agent.publish("status", snapshot=agent.build_snapshot())
    except (ConfigError, ValueError) as exc:
        filter_feedback = {
            "message_type": "error",
            "message": str(exc),
        }
        if "Settings YAML is malformed" in str(exc):
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    context = {
        "request": request,
        "current_agent": agent,
        "job_settings": agent._get_runtime_settings(),
        "filter_feedback": filter_feedback,
    }
    return templates.TemplateResponse(
        request,
        "partials/job_finder_filters.html",
        context,
        status_code=status_code,
    )


@router.post("/agents/job_finder/run", response_class=HTMLResponse)
async def run_job_finder(request: Request) -> HTMLResponse:
    """Trigger a manual crawl and return the results partial."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)

    try:
        summary = agent.run_crawl(trigger="manual")
        feedback = {
            "message_type": "success",
            "message": (
                f"Run finished with {summary.matched_count} matched jobs "
                f"and {len(summary.warnings)} warning(s)."
            ),
        }
        status_code = status.HTTP_200_OK
    except ConfigError as exc:
        summary = agent.last_run_summary
        feedback = {
            "message_type": "error",
            "message": str(exc),
        }
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    context = {
        "request": request,
        "feedback": feedback,
        "job_summary": summary,
        "jobs": agent.repository.list_ranked_jobs(),
        "job_warnings": summary.warnings if summary else [],
    }
    return templates.TemplateResponse(
        request,
        "partials/job_run_feedback.html",
        context,
        status_code=status_code,
    )


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    return int(stripped)
