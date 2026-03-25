"""Job Finder agent package."""

from backend.agents._registry import AgentRegistry
from backend.agents.job_finder.agent import JobFinderAgent


def register(registry: AgentRegistry) -> None:
    """Register the Job Finder agent with the shared registry."""

    registry.register(
        JobFinderAgent(
            settings=registry.get_settings("job_finder"),
            broker=registry.broker,
        )
    )
