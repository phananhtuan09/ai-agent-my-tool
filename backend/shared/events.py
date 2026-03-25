"""In-memory SSE fan-out for per-agent events."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any
import asyncio


class EventBroker:
    """Manages per-agent subscriber queues for SSE delivery."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(
            list
        )

    def register_agent(self, agent_name: str) -> None:
        """Ensure the agent has a subscriber bucket."""

        self._subscribers.setdefault(agent_name, [])

    def subscribe(self, agent_name: str) -> asyncio.Queue[dict[str, Any]]:
        """Create a queue for one SSE consumer."""

        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=20)
        self._subscribers[agent_name].append(queue)
        return queue

    def unsubscribe(self, agent_name: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """Remove a queue when the client disconnects."""

        subscribers = self._subscribers.get(agent_name, [])
        if queue in subscribers:
            subscribers.remove(queue)

    def publish(self, agent_name: str, event: Mapping[str, Any]) -> None:
        """Fan out an event to all current subscribers."""

        subscribers = list(self._subscribers.get(agent_name, []))
        payload = dict(event)
        for queue in subscribers:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                _drain_queue(queue)
                queue.put_nowait(payload)


def _drain_queue(queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Drop the oldest event when a client is slow."""

    try:
        queue.get_nowait()
    except asyncio.QueueEmpty:
        return
