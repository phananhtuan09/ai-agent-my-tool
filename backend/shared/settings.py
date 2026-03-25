"""YAML-backed runtime settings for the application."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any, Literal
import os

from apscheduler.triggers.cron import CronTrigger
from filelock import FileLock
from pydantic import BaseModel, Field, ValidationError, model_validator
import yaml

from backend.exceptions import ConfigError


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS_PATH = ROOT_DIR / "config" / "settings.yaml"


class JobSourceSettings(BaseModel):
    """Per-source crawl configuration for the Job Finder agent."""

    enabled: bool = True
    label: str = Field(min_length=1)
    simulate_failure: bool = False


class JobFilterSettings(BaseModel):
    """Hard and soft filter settings for the Job Finder agent."""

    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    locations: list[str] = Field(default_factory=list)
    must_have_frameworks: list[str] = Field(default_factory=list)
    nice_to_have_frameworks: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_salary_range(self) -> "JobFilterSettings":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return self


class JobFinderRuntimeSettings(BaseModel):
    """Job Finder-specific runtime configuration."""

    cron: str = Field(min_length=1)
    sources: dict[str, JobSourceSettings]
    filters: JobFilterSettings = Field(default_factory=JobFilterSettings)

    @model_validator(mode="after")
    def validate_cron(self) -> "JobFinderRuntimeSettings":
        try:
            CronTrigger.from_crontab(self.cron)
        except ValueError as exc:
            raise ValueError("cron must be a valid 5-field crontab string") from exc
        return self


class DailySchedulerRuntimeSettings(BaseModel):
    """Daily Schedule-specific runtime configuration."""

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

    enabled: bool = True
    label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    simulate_failure: bool = False


class CryptoAirdropRuntimeSettings(BaseModel):
    """Crypto Airdrop-specific runtime configuration."""

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


class AgentSettings(BaseModel):
    """Per-agent configuration persisted in settings.yaml."""

    provider: Literal["anthropic", "openai"]
    model: str = Field(min_length=1)
    api_key_env_var: str = Field(min_length=1)
    job_finder: JobFinderRuntimeSettings | None = None
    daily_scheduler: DailySchedulerRuntimeSettings | None = None
    crypto_airdrop: CryptoAirdropRuntimeSettings | None = None


class AppSettings(BaseModel):
    """Top-level application settings document."""

    agents: dict[str, AgentSettings]


def get_settings_path() -> Path:
    """Return the active settings path, allowing tests to override it."""

    override = os.environ.get("AI_AGENT_TOOL_SETTINGS_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_SETTINGS_PATH


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
        except ValidationError as exc:
            raise ConfigError(f"Invalid agent settings for '{agent_name}': {exc}") from exc

        agents[agent_name] = validated_agent.model_dump()
        settings_path.write_text(
            yaml.safe_dump(raw_data, sort_keys=False),
            encoding="utf-8",
        )

    return load_settings(settings_path)
