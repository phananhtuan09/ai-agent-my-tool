"""Agent auto-discovery and lookup."""

from __future__ import annotations

from pathlib import Path
import importlib
import pkgutil

from backend.agents.base_agent import BaseAgent
from backend.exceptions import AgentError, ConfigError
from backend.shared.events import EventBroker
from backend.shared.settings import AppSettings, AgentSettings, OpenAISettings


class AgentRegistry:
    """Discovers agent packages and keeps runtime instances."""

    def __init__(self, settings: AppSettings, broker: EventBroker) -> None:
        self._settings = settings
        self._broker = broker
        self._agents: dict[str, BaseAgent] = {}

    @property
    def broker(self) -> EventBroker:
        """Expose the shared event broker to register() hooks."""

        return self._broker

    def get_settings(self, agent_name: str) -> AgentSettings:
        """Return settings for an agent or fail fast."""

        try:
            return self._settings.agents[agent_name]
        except KeyError as exc:
            raise ConfigError(f"Missing settings for '{agent_name}'") from exc

    def get_openai_settings(self) -> OpenAISettings:
        """Return the current global OpenAI settings."""

        return self._settings.openai

    def register(self, agent: BaseAgent) -> None:
        """Register one concrete agent instance."""

        if agent.slug in self._agents:
            raise AgentError(f"Duplicate agent slug registered: {agent.slug}")
        self._agents[agent.slug] = agent

    def discover(self) -> None:
        """Import all non-private agent packages and invoke their register hook."""

        agents_dir = Path(__file__).resolve().parent
        for module_info in pkgutil.iter_modules([str(agents_dir)]):
            if module_info.name.startswith("_"):
                continue
            if module_info.name not in self._settings.agents:
                continue
            module = importlib.import_module(f"backend.agents.{module_info.name}")
            register = getattr(module, "register", None)
            if callable(register):
                register(self)

    def initialize(self) -> None:
        """Prepare runtime state for each discovered agent."""

        for agent in self.list_agents():
            agent.initialize()

    def replace_settings(self, settings: AppSettings) -> None:
        """Swap the root settings document and reload all agent clients."""

        self._settings = settings
        for agent in self._agents.values():
            agent.reload_settings(
                settings.agents[agent.slug],
                settings.openai,
            )

    def list_agents(self) -> list[BaseAgent]:
        """Return agents in title order for stable UI output."""

        return sorted(self._agents.values(), key=lambda agent: agent.title)

    def get(self, agent_name: str) -> BaseAgent:
        """Return a registered agent by slug."""

        try:
            return self._agents[agent_name]
        except KeyError as exc:
            raise AgentError(f"Unknown agent: {agent_name}") from exc
