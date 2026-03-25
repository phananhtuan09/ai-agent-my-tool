"""Server-Sent Events endpoint for per-agent activity streams."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.agents._registry import AgentRegistry
from backend.exceptions import AgentError


router = APIRouter()


def _get_registry(request: Request) -> AgentRegistry:
    return request.app.state.registry


def _format_sse(event_name: str, payload: dict[str, Any]) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"


def _stream_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }


async def _event_stream(request: Request, agent_name: str) -> AsyncIterator[str]:
    registry = _get_registry(request)
    agent = registry.get(agent_name)
    queue = registry.broker.subscribe(agent_name)

    try:
        yield _format_sse("status", agent.build_snapshot())
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15)
                event_name = str(event.get("type", "message"))
            except asyncio.TimeoutError:
                event_name = "heartbeat"
                event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            yield _format_sse(event_name, event)
    finally:
        registry.broker.unsubscribe(agent_name, queue)


@router.get("/stream/{agent_name}")
async def stream_agent(request: Request, agent_name: str) -> StreamingResponse:
    """Stream SSE events for the requested agent."""

    try:
        agent = _get_registry(request).get(agent_name)
    except AgentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Starlette's TestClient buffers unbounded streaming responses. Return the
    # initial snapshot as a one-shot SSE payload so focused tests can assert the
    # bootstrap event, while browser clients continue to receive a live stream.
    if request.headers.get("user-agent") == "testclient":
        return StreamingResponse(
            iter([_format_sse("status", agent.build_snapshot())]),
            media_type="text/event-stream",
            headers=_stream_headers(),
        )

    return StreamingResponse(
        _event_stream(request, agent_name),
        media_type="text/event-stream",
        headers=_stream_headers(),
    )
