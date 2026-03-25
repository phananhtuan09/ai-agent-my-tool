"""Page routes for the dashboard and agent views."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from backend.agents._registry import AgentRegistry
from backend.exceptions import AgentError


router = APIRouter()


def _get_registry(request: Request) -> AgentRegistry:
    return request.app.state.registry


def _get_templates(request: Request):
    return request.app.state.templates


def _base_context(request: Request) -> dict[str, object]:
    registry = _get_registry(request)
    return {
        "request": request,
        "agents": registry.list_agents(),
        "current_agent": None,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the registry-backed dashboard."""

    context = _base_context(request)
    context.update(
        {
            "page_title": "AI Agent Tool",
            "page_description": "A unified control room for three independent automation agents.",
        }
    )
    return _get_templates(request).TemplateResponse(request, "dashboard.html", context)


@router.get("/agents/{agent_name}", response_class=HTMLResponse)
async def agent_page(request: Request, agent_name: str) -> HTMLResponse:
    """Render one agent console page."""

    registry = _get_registry(request)
    try:
        agent = registry.get(agent_name)
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    context = _base_context(request)
    context.update(
        {
            "page_title": agent.title,
            "current_agent": agent,
            **agent.build_page_context(),
        }
    )
    return _get_templates(request).TemplateResponse(
        request,
        agent.template_name,
        context,
    )
