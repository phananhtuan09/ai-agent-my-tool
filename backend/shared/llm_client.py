"""Lightweight LLM client descriptor used by the foundation slice."""

from __future__ import annotations

from dataclasses import dataclass
import os

from backend.shared.settings import AgentSettings


@dataclass(slots=True)
class LLMClient:
    """Stores the active model selection for an agent."""

    provider: str
    model: str
    api_key_env_var: str

    @classmethod
    def from_settings(cls, settings: AgentSettings) -> "LLMClient":
        """Create a client descriptor from validated settings."""

        return cls(
            provider=settings.provider,
            model=settings.model,
            api_key_env_var=settings.api_key_env_var,
        )

    @property
    def is_configured(self) -> bool:
        """Whether the backing API key exists in the current environment."""

        return bool(os.environ.get(self.api_key_env_var))

    def to_summary(self) -> dict[str, str | bool]:
        """Return a small UI-ready summary of the current config."""

        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_env_var": self.api_key_env_var,
            "is_configured": self.is_configured,
        }
