"""Daily Scheduler agent package."""

from backend.agents._registry import AgentRegistry
from backend.agents.daily_scheduler.agent import DailySchedulerAgent


def register(registry: AgentRegistry) -> None:
    """Register the Daily Scheduler agent with the shared registry."""

    registry.register(
        DailySchedulerAgent(
            settings=registry.get_settings("daily_scheduler"),
            broker=registry.broker,
        )
    )
