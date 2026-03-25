"""HTMX endpoints for the Daily Schedule agent."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from backend.agents.daily_scheduler.agent import DailySchedulerAgent
from backend.exceptions import AgentError, ConfigError
from backend.shared.settings import save_agent_settings


router = APIRouter()


def _get_templates(request: Request):
    return request.app.state.templates


def _resolve_agent(request: Request) -> DailySchedulerAgent:
    registry = request.app.state.registry
    try:
        agent = registry.get("daily_scheduler")
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return agent


@router.get("/agents/daily_scheduler/controls", response_class=HTMLResponse)
async def get_daily_scheduler_controls(request: Request) -> HTMLResponse:
    """Render the Daily Schedule controls partial."""

    agent = _resolve_agent(request)
    context = {
        "request": request,
        "current_agent": agent,
        "schedule_settings": agent._get_runtime_settings(),
        "schedule_feedback": None,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/daily_scheduler_controls.html",
        context,
    )


@router.post("/agents/daily_scheduler/settings", response_class=HTMLResponse)
async def save_daily_scheduler_settings(
    request: Request,
    reminder_cron: str = Form(...),
    reset_cron: str = Form(...),
    workday_start: str = Form(...),
    focus_break_minutes: str = Form(...),
    default_task_minutes: str = Form(...),
) -> HTMLResponse:
    """Persist nested Daily Schedule runtime settings."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)

    try:
        payload = {
            "daily_scheduler": {
                "reminder_cron": reminder_cron.strip(),
                "reset_cron": reset_cron.strip(),
                "workday_start": workday_start.strip(),
                "focus_break_minutes": int(focus_break_minutes.strip()),
                "default_task_minutes": int(default_task_minutes.strip()),
            }
        }
        settings = save_agent_settings("daily_scheduler", payload)
        updated_settings = settings.agents["daily_scheduler"]
        agent.reload_settings(updated_settings)
        agent.register_jobs(request.app.state.scheduler)
        agent.publish("status", snapshot=agent.build_snapshot())
        schedule_feedback = {
            "message_type": "success",
            "message": "Daily schedule settings saved and reloaded.",
        }
        status_code = status.HTTP_200_OK
    except (ConfigError, ValueError) as exc:
        schedule_feedback = {
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
        "schedule_settings": agent._get_runtime_settings(),
        "schedule_feedback": schedule_feedback,
    }
    return templates.TemplateResponse(
        request,
        "partials/daily_scheduler_controls.html",
        context,
        status_code=status_code,
    )


@router.post("/agents/daily_scheduler/chat", response_class=HTMLResponse)
async def post_daily_scheduler_chat(
    request: Request,
    message: str = Form(...),
) -> HTMLResponse:
    """Handle Daily Schedule chat submissions and return refreshed partials."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)

    try:
        result = agent.handle_chat(message)
        chat_feedback = {
            "message_type": "success",
            "message": result["reply"],
        }
        status_code = status.HTTP_200_OK
    except ConfigError as exc:
        chat_feedback = {
            "message_type": "error",
            "message": str(exc),
        }
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    context = {
        "request": request,
        "chat_feedback": chat_feedback,
        "schedule_tasks": agent.repository.list_tasks(),
        "schedule_messages": agent.repository.list_messages(),
        "awaiting_overdue_resolution": agent._get_pending_overdue_task(
            agent.repository.list_tasks()
        )
        is not None,
    }
    return templates.TemplateResponse(
        request,
        "partials/daily_schedule_chat.html",
        context,
        status_code=status_code,
    )
