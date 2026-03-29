"""YAML-backed runtime settings for the application."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import os
import re

from apscheduler.triggers.cron import CronTrigger
from filelock import FileLock
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
import yaml

from backend.exceptions import ConfigError


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS_PATH = ROOT_DIR / "config" / "settings.yaml"
DEFAULT_ENV_PATH = ROOT_DIR / "config" / ".env"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"


def _normalize_model_name(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("model must not be empty")
    return normalized


class DailySchedulerRuntimeSettings(BaseModel):
    """Daily Schedule-specific runtime configuration."""

    model_config = ConfigDict(extra="forbid")

    reminder_cron: str = Field(min_length=1)
    reset_cron: str = Field(min_length=1)
    workday_start: str = Field(min_length=1)
    focus_break_minutes: int = Field(default=10, ge=0)
    default_task_minutes: int = Field(default=45, ge=15)

    @model_validator(mode="after")
    def validate_runtime(self) -> "DailySchedulerRuntimeSettings":
        for field_name in ("reminder_cron", "reset_cron"):
            try:
                CronTrigger.from_crontab(getattr(self, field_name))
            except ValueError as exc:
                raise ValueError(f"{field_name} must be a valid 5-field crontab string") from exc

        try:
            datetime.strptime(self.workday_start, "%H:%M")
        except ValueError as exc:
            raise ValueError("workday_start must use HH:MM 24-hour format") from exc
        return self


class CryptoAirdropSourceSettings(BaseModel):
    """Per-source crawl configuration for the Crypto Airdrop agent."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    simulate_failure: bool = False


class CryptoAirdropRuntimeSettings(BaseModel):
    """Crypto Airdrop-specific runtime configuration."""

    model_config = ConfigDict(extra="forbid")

    cron: str = Field(min_length=1)
    sources: dict[str, CryptoAirdropSourceSettings]

    @model_validator(mode="after")
    def validate_runtime(self) -> "CryptoAirdropRuntimeSettings":
        try:
            CronTrigger.from_crontab(self.cron)
        except ValueError as exc:
            raise ValueError("cron must be a valid 5-field crontab string") from exc

        allowed_sources = {"airdrops_io", "cryptorank", "defillama"}
        invalid_sources = set(self.sources) - allowed_sources
        if invalid_sources:
            invalid = ", ".join(sorted(invalid_sources))
            raise ValueError(f"Unsupported crypto airdrop source(s): {invalid}")
        return self


class OpenAISettings(BaseModel):
    """Global OpenAI configuration persisted in settings.yaml."""

    model_config = ConfigDict(extra="forbid")

    base_url: str = Field(min_length=1)
    default_model: str = Field(min_length=1)
    available_models: list[str] = Field(default_factory=list)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        normalized = value.strip().rstrip("/")
        if not normalized:
            raise ValueError("base_url must not be empty")
        return normalized

    @field_validator("default_model")
    @classmethod
    def validate_default_model(cls, value: str) -> str:
        return _normalize_model_name(value)

    @field_validator("available_models")
    @classmethod
    def validate_available_models(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            model_name = _normalize_model_name(item)
            if model_name in seen:
                continue
            seen.add(model_name)
            normalized.append(model_name)
        return normalized


class AgentSettings(BaseModel):
    """Per-agent configuration persisted in settings.yaml."""

    model_config = ConfigDict(extra="forbid")

    model: str | None = None
    daily_scheduler: DailySchedulerRuntimeSettings | None = None
    crypto_airdrop: CryptoAirdropRuntimeSettings | None = None

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_model_name(value)


class AppSettings(BaseModel):
    """Top-level application settings document."""

    model_config = ConfigDict(extra="forbid")

    openai: OpenAISettings
    agents: dict[str, AgentSettings]


def get_settings_path() -> Path:
    """Return the active settings path, allowing tests to override it."""

    override = os.environ.get("AI_AGENT_TOOL_SETTINGS_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_SETTINGS_PATH


def get_env_path() -> Path:
    """Return the active env path, allowing tests to override it."""

    override = os.environ.get("AI_AGENT_TOOL_ENV_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_ENV_PATH


def resolve_agent_storage_path(default_path: Path, agent_name: str) -> Path:
    """Return the storage path for one agent in the active runtime context."""

    settings_path = get_settings_path()
    if settings_path != DEFAULT_SETTINGS_PATH:
        return settings_path.parent / f"{agent_name}-memory.db"
    return default_path


def load_settings(path: Path | None = None) -> AppSettings:
    """Load and validate the current application settings document."""

    settings_path = path or get_settings_path()
    if not settings_path.exists():
        raise ConfigError(f"Settings file not found: {settings_path}")

    try:
        data = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
        return AppSettings.model_validate(data)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Settings YAML is malformed: {settings_path}") from exc
    except ValidationError as exc:
        raise ConfigError(f"Settings validation failed: {exc}") from exc


def load_env_value(name: str, path: Path | None = None) -> str | None:
    """Return a persisted env value without mutating process environment."""

    env_path = path or get_env_path()
    if not env_path.exists():
        return None

    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=\s*(.*)\s*$")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        raw_value = match.group(1).strip()
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in {'"', "'"}:
            return raw_value[1:-1]
        return raw_value
    return None


def is_openai_api_key_configured(path: Path | None = None) -> bool:
    """Report whether the OpenAI API key is available in memory or on disk."""

    return bool(get_openai_api_key(path))


def get_openai_api_key(path: Path | None = None) -> str | None:
    """Return the current OpenAI API key from memory or the persisted env file."""

    return os.environ.get(OPENAI_API_KEY_ENV_VAR) or load_env_value(OPENAI_API_KEY_ENV_VAR, path)


def save_openai_settings(
    payload: dict[str, Any],
    *,
    api_key: str | None = None,
    path: Path | None = None,
    env_path: Path | None = None,
) -> AppSettings:
    """Persist the global OpenAI config and optionally rotate the API key."""

    settings_path = path or get_settings_path()
    current_env_path = env_path or get_env_path()
    if not settings_path.exists():
        raise ConfigError(f"Settings file not found: {settings_path}")

    lock = FileLock(f"{settings_path}.lock")
    with lock:
        try:
            raw_data = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Settings YAML is malformed: {settings_path}") from exc

        current_payload = dict(raw_data.get("openai") or {})
        current_payload.update(payload)

        try:
            validated_openai = OpenAISettings.model_validate(current_payload)
            raw_data["openai"] = validated_openai.model_dump()
            validated_settings = AppSettings.model_validate(raw_data)
        except ValidationError as exc:
            raise ConfigError(f"Invalid OpenAI settings: {exc}") from exc

        yaml_text = yaml.safe_dump(validated_settings.model_dump(), sort_keys=False)
        previous_env_exists = current_env_path.exists()
        previous_env_text = (
            current_env_path.read_text(encoding="utf-8") if previous_env_exists else ""
        )
        next_env_text = previous_env_text
        normalized_api_key = api_key.strip() if api_key is not None else None
        if normalized_api_key is not None:
            if not normalized_api_key:
                raise ConfigError("api_key must not be empty when provided.")
            next_env_text = _upsert_env_value(
                previous_env_text,
                OPENAI_API_KEY_ENV_VAR,
                normalized_api_key,
            )

        try:
            if normalized_api_key is not None:
                current_env_path.parent.mkdir(parents=True, exist_ok=True)
                current_env_path.write_text(next_env_text, encoding="utf-8")
            settings_path.write_text(yaml_text, encoding="utf-8")
        except OSError as exc:
            if normalized_api_key is not None:
                _restore_env_file(current_env_path, previous_env_exists, previous_env_text)
            raise ConfigError(f"Failed to persist OpenAI settings: {exc}") from exc

    if normalized_api_key is not None:
        os.environ[OPENAI_API_KEY_ENV_VAR] = normalized_api_key
    return load_settings(settings_path)


def save_agent_settings(
    agent_name: str,
    payload: dict[str, Any],
    path: Path | None = None,
) -> AppSettings:
    """Persist one agent's configuration and re-validate the full document."""

    settings_path = path or get_settings_path()
    if not settings_path.exists():
        raise ConfigError(f"Settings file not found: {settings_path}")

    lock = FileLock(f"{settings_path}.lock")
    with lock:
        try:
            raw_data = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Settings YAML is malformed: {settings_path}") from exc

        agents = raw_data.setdefault("agents", {})
        if agent_name not in agents:
            raise ConfigError(f"Agent settings not found for '{agent_name}'")

        current_payload = dict(agents[agent_name])
        current_payload.update(payload)

        try:
            validated_agent = AgentSettings.model_validate(current_payload)
            agents[agent_name] = validated_agent.model_dump()
            validated_settings = AppSettings.model_validate(raw_data)
        except ValidationError as exc:
            raise ConfigError(f"Invalid agent settings for '{agent_name}': {exc}") from exc

        settings_path.write_text(
            yaml.safe_dump(validated_settings.model_dump(), sort_keys=False),
            encoding="utf-8",
        )

    return load_settings(settings_path)


def _upsert_env_value(content: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=.*$", re.MULTILINE)
    line = f"{name}={value}"
    if pattern.search(content):
        return pattern.sub(line, content)
    if not content:
        return f"{line}\n"
    separator = "" if content.endswith("\n") else "\n"
    return f"{content}{separator}{line}\n"


def _restore_env_file(path: Path, existed: bool, content: str) -> None:
    if existed:
        path.write_text(content, encoding="utf-8")
        return
    if path.exists():
        path.unlink()
