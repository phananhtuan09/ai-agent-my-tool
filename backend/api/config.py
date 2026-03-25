"""HTMX endpoints for the agent configuration modal."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from backend.agents._registry import AgentRegistry
from backend.exceptions import AgentError, ConfigError
from backend.shared.settings import save_agent_settings


router = APIRouter()


def _get_registry(request: Request) -> AgentRegistry:
    return request.app.state.registry


def _get_templates(request: Request):
    return request.app.state.templates


def _resolve_agent(request: Request, agent_name: str):
    registry = _get_registry(request)
    try:
        return registry.get(agent_name)
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/agents/{agent_name}/config", response_class=HTMLResponse)
async def config_modal(request: Request, agent_name: str) -> HTMLResponse:
    """Render the config modal for one agent."""

    agent = _resolve_agent(request, agent_name)
    context = {
        "request": request,
        "agent": agent,
        "agent_config": agent.settings,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/config_modal.html",
        context,
    )


@router.post("/agents/{agent_name}/config", response_class=HTMLResponse)
async def save_config(
    request: Request,
    agent_name: str,
    provider: str = Form(...),
    model: str = Form(...),
    api_key_env_var: str = Form(...),
) -> HTMLResponse:
    """Persist new config values and hot-swap the agent runtime."""

    agent = _resolve_agent(request, agent_name)
    templates = _get_templates(request)

    try:
        settings = save_agent_settings(
            agent_name,
            {
                "provider": provider,
                "model": model,
                "api_key_env_var": api_key_env_var,
            },
        )
        updated_settings = settings.agents[agent_name]
        agent.reload_settings(updated_settings)
        agent.publish(
            "notify",
            message=f"{agent.title} config reloaded with {updated_settings.provider}:{updated_settings.model}.",
        )
        agent.publish("status", snapshot=agent.build_snapshot())
        message = "Configuration saved. The agent runtime now uses the updated model selection."
        message_type = "success"
        status_code = status.HTTP_200_OK
    except ConfigError as exc:
        message = str(exc)
        message_type = "error"
        if "Settings YAML is malformed" in message:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    context = {
        "request": request,
        "message": message,
        "message_type": message_type,
    }
    return templates.TemplateResponse(
        request,
        "partials/config_feedback.html",
        context,
        status_code=status_code,
    )
