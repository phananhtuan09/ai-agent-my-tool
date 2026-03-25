"""Domain exception types used across the application."""


class AgentError(Exception):
    """Base exception for agent lifecycle and runtime failures."""


class ConfigError(AgentError):
    """Raised when settings or environment configuration is invalid."""


class CrawlError(AgentError):
    """Raised when a crawler cannot complete its work."""


class LLMError(AgentError):
    """Raised when the configured LLM provider cannot serve a request."""
