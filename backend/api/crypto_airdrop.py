"""HTMX endpoints for the Crypto Airdrop agent."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from backend.agents.crypto_airdrop.agent import CryptoAirdropAgent
from backend.exceptions import AgentError, ConfigError
from backend.shared.settings import save_agent_settings


router = APIRouter()


def _get_templates(request: Request):
    return request.app.state.templates


def _resolve_agent(request: Request) -> CryptoAirdropAgent:
    registry = request.app.state.registry
    try:
        agent = registry.get("crypto_airdrop")
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return agent


@router.get("/agents/crypto_airdrop/controls", response_class=HTMLResponse)
async def get_crypto_airdrop_controls(request: Request) -> HTMLResponse:
    """Render the Crypto Airdrop controls partial."""

    agent = _resolve_agent(request)
    context = {
        "request": request,
        "current_agent": agent,
        "airdrop_settings": agent._get_runtime_settings(),
        "airdrop_feedback": None,
    }
    return _get_templates(request).TemplateResponse(
        request,
        "partials/crypto_airdrop_controls.html",
        context,
    )


@router.post("/agents/crypto_airdrop/settings", response_class=HTMLResponse)
async def save_crypto_airdrop_settings(
    request: Request,
    cron: str = Form(...),
    airdrops_io_enabled: str | None = Form(default=None),
    cryptorank_enabled: str | None = Form(default=None),
    defillama_enabled: str | None = Form(default=None),
) -> HTMLResponse:
    """Persist nested Crypto Airdrop runtime settings."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)
    runtime = agent._get_runtime_settings()

    try:
        payload = {
            "crypto_airdrop": {
                "cron": cron.strip(),
                "sources": {
                    "airdrops_io": {
                        "enabled": airdrops_io_enabled == "on",
                        "label": runtime.sources["airdrops_io"].label,
                        "url": runtime.sources["airdrops_io"].url,
                        "simulate_failure": runtime.sources["airdrops_io"].simulate_failure,
                    },
                    "cryptorank": {
                        "enabled": cryptorank_enabled == "on",
                        "label": runtime.sources["cryptorank"].label,
                        "url": runtime.sources["cryptorank"].url,
                        "simulate_failure": runtime.sources["cryptorank"].simulate_failure,
                    },
                    "defillama": {
                        "enabled": defillama_enabled == "on",
                        "label": runtime.sources["defillama"].label,
                        "url": runtime.sources["defillama"].url,
                        "simulate_failure": runtime.sources["defillama"].simulate_failure,
                    },
                },
            }
        }
        settings = save_agent_settings("crypto_airdrop", payload)
        updated_settings = settings.agents["crypto_airdrop"]
        agent.reload_settings(updated_settings)
        agent.register_jobs(request.app.state.scheduler)
        agent.publish("status", snapshot=agent.build_snapshot())
        airdrop_feedback = {
            "message_type": "success",
            "message": "Crypto airdrop settings saved and reloaded.",
        }
        status_code = status.HTTP_200_OK
    except (ConfigError, ValueError) as exc:
        airdrop_feedback = {
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
        "airdrop_settings": agent._get_runtime_settings(),
        "airdrop_feedback": airdrop_feedback,
    }
    return templates.TemplateResponse(
        request,
        "partials/crypto_airdrop_controls.html",
        context,
        status_code=status_code,
    )


@router.post("/agents/crypto_airdrop/run", response_class=HTMLResponse)
async def run_crypto_airdrop(request: Request) -> HTMLResponse:
    """Trigger a manual airdrop crawl and return refreshed partials."""

    agent = _resolve_agent(request)
    templates = _get_templates(request)

    try:
        summary = agent.run_crawl(trigger="manual")
        feedback = {
            "message_type": "success",
            "message": (
                f"Run finished with {summary.matched_count} ranked airdrops and "
                f"{len(summary.warnings)} warning(s)."
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
        "airdrop_summary": summary,
        "airdrops": agent.repository.list_latest_airdrops(),
        "airdrop_messages": agent.repository.list_messages(),
        "airdrop_warnings": summary.warnings if summary else [],
    }
    return templates.TemplateResponse(
        request,
        "partials/crypto_airdrop_run_feedback.html",
        context,
        status_code=status_code,
    )


@router.post("/agents/crypto_airdrop/chat", response_class=HTMLResponse)
async def post_crypto_airdrop_chat(
    request: Request,
    message: str = Form(...),
) -> HTMLResponse:
    """Handle Crypto Airdrop chat submissions and return refreshed partials."""

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
        "airdrops": (
            agent.repository.list_latest_airdrops()
            if agent.last_filtered_airdrops is None
            else agent.last_filtered_airdrops
        ),
        "airdrop_messages": agent.repository.list_messages(),
        "airdrop_summary": agent.last_run_summary,
        "airdrop_warnings": agent.last_run_summary.warnings if agent.last_run_summary else [],
    }
    return templates.TemplateResponse(
        request,
        "partials/crypto_airdrop_chat.html",
        context,
        status_code=status_code,
    )
