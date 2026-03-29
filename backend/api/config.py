"""Routes for the global config page and per-agent model modal."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from backend.agents._registry import AgentRegistry
from backend.exceptions import AgentError, ConfigError
from backend.shared.openai_catalog import fetch_openai_models
from backend.shared.settings import (
    get_openai_api_key,
    is_openai_api_key_configured,
    save_agent_settings,
    save_openai_settings,
)


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


def _build_model_options(
    available_models: list[str],
    *fallback_models: str | None,
) -> list[str]:
    options: list[str] = []
    seen: set[str] = set()
    for candidate in [*available_models, *fallback_models]:
        if candidate is None:
            continue
        normalized = candidate.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        options.append(normalized)
    return options


def _build_config_context(
    request: Request,
    *,
    message: str | None = None,
    message_type: str | None = None,
) -> dict[str, object]:
    registry = _get_registry(request)
    openai_config = registry.get_openai_settings()
    available_models = _build_model_options(
        openai_config.available_models,
        openai_config.default_model,
    )
    return {
        "request": request,
        "agents": registry.list_agents(),
        "current_agent": None,
        "current_page": "config",
        "page_title": "OpenAI Config",
        "page_context": "Global configuration",
        "page_description": "Manage API access, verify connectivity, and refresh the shared model catalog.",
        "openai_config": openai_config,
        "api_key_configured": is_openai_api_key_configured(),
        "available_models": available_models,
        "selected_model": openai_config.default_model,
        "message": message,
        "message_type": message_type,
    }


def _render_config_feedback(
    request: Request,
    *,
    message: str,
    message_type: str,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    context = {
        "request": request,
        "message": message,
        "message_type": message_type,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/config_feedback.html",
        context,
        status_code=status_code,
    )


def _render_model_field(
    request: Request,
    *,
    available_models: list[str],
    selected_model: str,
    message: str,
    message_type: str,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    context = {
        "request": request,
        "available_models": available_models,
        "selected_model": selected_model,
        "message": message,
        "message_type": message_type,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/openai_model_field.html",
        context,
        status_code=status_code,
    )


def _resolve_api_key(submitted_api_key: str) -> str:
    candidate = submitted_api_key.strip()
    if candidate:
        return candidate
    stored_api_key = get_openai_api_key()
    if stored_api_key:
        return stored_api_key
    raise ConfigError("OpenAI API key is required before testing or fetching models.")


def _refresh_registry(request: Request, settings, *, message: str) -> None:
    registry = _get_registry(request)
    registry.replace_settings(settings)
    for agent in registry.list_agents():
        agent.publish("notify", message=message)
        agent.publish("status", snapshot=agent.build_snapshot())


@router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request) -> HTMLResponse:
    """Render the dedicated OpenAI config page."""

    context = _build_config_context(request)
    return _get_templates(request).TemplateResponse(request, "config.html", context)


@router.post("/config/openai", response_class=HTMLResponse)
async def save_openai_config(
    request: Request,
    base_url: str = Form(...),
    default_model: str = Form(...),
    api_key: str = Form(""),
) -> HTMLResponse:
    """Persist the global OpenAI config and hot-swap all agents."""

    try:
        settings = save_openai_settings(
            {
                "base_url": base_url.strip(),
                "default_model": default_model.strip(),
            },
            api_key=api_key if api_key.strip() else None,
        )
        _refresh_registry(
            request,
            settings,
            message=f"OpenAI settings reloaded with {settings.openai.default_model}.",
        )
        return _render_config_feedback(
            request,
            message="OpenAI settings saved.",
            message_type="success",
        )
    except ConfigError as exc:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if "Settings YAML is malformed" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return _render_config_feedback(
            request,
            message=str(exc),
            message_type="error",
            status_code=status_code,
        )


@router.post("/config/openai/test", response_class=HTMLResponse)
async def test_openai_config(
    request: Request,
    base_url: str = Form(...),
    api_key: str = Form(""),
) -> HTMLResponse:
    """Validate one submitted OpenAI-compatible endpoint without persisting it."""

    try:
        models = await fetch_openai_models(base_url.strip(), _resolve_api_key(api_key))
        return _render_model_field(
            request,
            available_models=models,
            selected_model=models[0],
            message=f"API connection OK. Found {len(models)} model(s).",
            message_type="success",
        )
    except ConfigError as exc:
        openai_config = _get_registry(request).get_openai_settings()
        return _render_model_field(
            request,
            available_models=_build_model_options(
                openai_config.available_models,
                openai_config.default_model,
            ),
            selected_model=openai_config.default_model,
            message=str(exc),
            message_type="error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.post("/config/openai/fetch-models", response_class=HTMLResponse)
async def fetch_openai_model_catalog(
    request: Request,
    base_url: str = Form(...),
    default_model: str = Form(...),
    api_key: str = Form(""),
) -> HTMLResponse:
    """Fetch and persist the shared model catalog from an OpenAI-compatible endpoint."""

    try:
        normalized_base_url = base_url.strip()
        models = await fetch_openai_models(normalized_base_url, _resolve_api_key(api_key))
        normalized_default_model = default_model.strip()
        persisted_default_model = (
            normalized_default_model if normalized_default_model in models else models[0]
        )
        settings = save_openai_settings(
            {
                "base_url": normalized_base_url,
                "default_model": persisted_default_model,
                "available_models": models,
            },
            api_key=api_key if api_key.strip() else None,
        )
        _refresh_registry(
            request,
            settings,
            message=f"OpenAI model catalog refreshed with {len(models)} model(s).",
        )
        return _render_model_field(
            request,
            available_models=models,
            selected_model=persisted_default_model,
            message=f"Fetched {len(models)} model(s) from the API.",
            message_type="success",
        )
    except ConfigError as exc:
        openai_config = _get_registry(request).get_openai_settings()
        return _render_model_field(
            request,
            available_models=_build_model_options(
                openai_config.available_models,
                openai_config.default_model,
            ),
            selected_model=openai_config.default_model,
            message=str(exc),
            message_type="error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.get("/agents/{agent_name}/config", response_class=HTMLResponse)
async def config_modal(request: Request, agent_name: str) -> HTMLResponse:
    """Render the model-only config modal for one agent from the shared catalog."""

    agent = _resolve_agent(request, agent_name)
    openai_config = _get_registry(request).get_openai_settings()
    context = {
        "request": request,
        "agent": agent,
        "agent_config": agent.settings,
        "openai_config": openai_config,
        "model_options": _build_model_options(
            openai_config.available_models,
            openai_config.default_model,
            agent.settings.model,
        ),
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
    model: str = Form(""),
) -> HTMLResponse:
    """Persist a model override and hot-swap the agent runtime."""

    registry = _get_registry(request)
    agent = _resolve_agent(request, agent_name)
    openai_config = registry.get_openai_settings()
    normalized_model = model.strip() or None
    available_models = _build_model_options(
        openai_config.available_models,
        openai_config.default_model,
        agent.settings.model,
    )

    if normalized_model and normalized_model not in available_models:
        return _render_config_feedback(
            request,
            message="Selected model is not in the fetched config catalog.",
            message_type="error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        settings = save_agent_settings(agent_name, {"model": normalized_model})
        registry.replace_settings(settings)
        updated_settings = settings.agents[agent_name]
        effective_model = updated_settings.model or settings.openai.default_model
        model_scope = "custom override" if updated_settings.model else "global default"
        agent.publish(
            "notify",
            message=(
                f"{agent.title} model reloaded with {effective_model} "
                f"from the {model_scope}."
            ),
        )
        agent.publish("status", snapshot=agent.build_snapshot())
        return _render_config_feedback(
            request,
            message="Model selection saved.",
            message_type="success",
        )
    except ConfigError as exc:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if "Settings YAML is malformed" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return _render_config_feedback(
            request,
            message=str(exc),
            message_type="error",
            status_code=status_code,
        )
