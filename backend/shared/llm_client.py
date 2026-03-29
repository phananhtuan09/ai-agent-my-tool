"""Lightweight LLM client descriptor used by the foundation slice."""

from __future__ import annotations

from dataclasses import dataclass
import os

from backend.shared.settings import (
    AgentSettings,
    OPENAI_API_KEY_ENV_VAR,
    OpenAISettings,
    load_env_value,
)


@dataclass(slots=True)
class LLMClient:
    """Stores the active model selection for an agent."""

    provider: str
    base_url: str
    model: str
    model_source: str
    api_key_name: str = OPENAI_API_KEY_ENV_VAR

    @classmethod
    def from_settings(
        cls,
        settings: AgentSettings,
        openai_settings: OpenAISettings,
    ) -> "LLMClient":
        """Create a client descriptor from validated settings."""

        return cls(
            provider="openai",
            base_url=openai_settings.base_url,
            model=settings.model or openai_settings.default_model,
            model_source="override" if settings.model else "default",
        )

    @property
    def is_configured(self) -> bool:
        """Whether the backing API key exists in the current environment."""

        return bool(os.environ.get(self.api_key_name) or load_env_value(self.api_key_name))

    def to_summary(self) -> dict[str, str | bool]:
        """Return a small UI-ready summary of the current config."""

        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "model_source": self.model_source,
            "is_configured": self.is_configured,
        }
