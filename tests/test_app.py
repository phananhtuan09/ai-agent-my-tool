from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from backend.exceptions import ConfigError
from backend.main import create_app
from backend.shared.settings import load_settings


TEST_SETTINGS = """\
openai:
  base_url: https://api.openai.com/v1
  default_model: gpt-5
  available_models:
    - gpt-5
    - gpt-5-mini
    - gpt-4.1-mini
agents:
  daily_scheduler:
    model: gpt-5-mini
    daily_scheduler:
      reminder_cron: "0 * * * *"
      reset_cron: "0 0 * * *"
      workday_start: "09:00"
      focus_break_minutes: 10
      default_task_minutes: 45
  crypto_airdrop:
    model: gpt-4.1-mini
    crypto_airdrop:
      cron: "0 */6 * * *"
      sources:
        airdrops_io:
          enabled: true
          label: airdrops.io
          url: https://airdrops.io
        cryptorank:
          enabled: true
          label: CryptoRank
          url: https://cryptorank.io
        defillama:
          enabled: true
          label: DeFiLlama
          url: https://defillama.com
"""


def _build_client(tmp_path: Path, monkeypatch) -> tuple[TestClient, Path, Path]:
    settings_path = tmp_path / "settings.yaml"
    env_path = tmp_path / ".env"
    settings_path.write_text(TEST_SETTINGS, encoding="utf-8")
    monkeypatch.setenv("AI_AGENT_TOOL_SETTINGS_PATH", str(settings_path))
    monkeypatch.setenv("AI_AGENT_TOOL_ENV_PATH", str(env_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return TestClient(create_app()), settings_path, env_path


def test_dashboard_lists_active_agents_without_job_finder(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Daily Schedule" in response.text
    assert "Crypto Airdrop" in response.text
    assert "Job Finder" not in response.text
    assert 'href="/config"' in response.text


def test_config_page_renders_openai_form(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/config")

    assert response.status_code == 200
    assert "OpenAI config" in response.text
    assert 'name="base_url"' in response.text
    assert "Test API" in response.text


def test_openai_test_fetches_models(tmp_path: Path, monkeypatch) -> None:
    client, _, env_path = _build_client(tmp_path, monkeypatch)
    env_path.write_text("OPENAI_API_KEY=sk-existing\n", encoding="utf-8")
    async def _fake_fetch_openai_models(base_url: str, api_key: str) -> list[str]:
        return ["gpt-5", "gpt-5-mini"]

    monkeypatch.setattr("backend.api.config.fetch_openai_models", _fake_fetch_openai_models)

    with client:
        response = client.post(
            "/config/openai/test",
            data={
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
            },
        )

    assert response.status_code == 200
    assert "API connection OK. Found 2 model(s)." in response.text
    assert "gpt-5-mini" in response.text


def test_openai_config_update_persists_and_hot_swaps(tmp_path: Path, monkeypatch) -> None:
    client, settings_path, env_path = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/config/openai",
            data={
                "base_url": "https://proxy.openai.local/v1",
                "default_model": "gpt-5-mini",
                "api_key": "sk-test-123",
            },
        )
        snapshot = client.app.state.registry.get("daily_scheduler").build_snapshot()

    saved_text = settings_path.read_text(encoding="utf-8")
    saved_env = env_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "OpenAI settings saved" in response.text
    assert "base_url: https://proxy.openai.local/v1" in saved_text
    assert "default_model: gpt-5-mini" in saved_text
    assert "OPENAI_API_KEY=sk-test-123" in saved_env
    assert snapshot["provider"] == "openai"
    assert snapshot["model"] == "gpt-5-mini"
    assert snapshot["base_url"] == "https://proxy.openai.local/v1"
    assert snapshot["is_configured"] is True


def test_fetch_models_persists_catalog_for_agent_modal(tmp_path: Path, monkeypatch) -> None:
    client, settings_path, _ = _build_client(tmp_path, monkeypatch)

    async def _fake_fetch_openai_models(base_url: str, api_key: str) -> list[str]:
        return ["gpt-5", "gpt-5-mini", "gpt-4.1-mini", "gpt-4.1"]

    monkeypatch.setattr("backend.api.config.fetch_openai_models", _fake_fetch_openai_models)

    with client:
        fetch_response = client.post(
            "/config/openai/fetch-models",
            data={
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-test-123",
                "default_model": "gpt-5-mini",
            },
        )
        response = client.get("/agents/daily_scheduler/config")

    saved_text = settings_path.read_text(encoding="utf-8")

    assert fetch_response.status_code == 200
    assert "Fetched 4 model(s)" in fetch_response.text
    assert response.status_code == 200
    assert "gpt-4.1" in response.text
    assert "gpt-5-mini" in response.text
    assert "available_models:" in saved_text
    assert "OPENAI_API_KEY=sk-test-123" not in saved_text


def test_agent_model_override_persists_and_hot_swaps(tmp_path: Path, monkeypatch) -> None:
    client, settings_path, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/daily_scheduler/config",
            data={"model": "gpt-4.1-mini"},
        )
        snapshot = client.app.state.registry.get("daily_scheduler").build_snapshot()

    saved_text = settings_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "Model selection saved" in response.text
    assert "model: gpt-4.1-mini" in saved_text
    assert snapshot["model"] == "gpt-4.1-mini"
    assert snapshot["model_source"] == "override"


def test_agent_model_can_fall_back_to_global_default(tmp_path: Path, monkeypatch) -> None:
    client, settings_path, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post(
            "/agents/daily_scheduler/config",
            data={"model": "gpt-4.1-mini"},
        )
        response = client.post(
            "/agents/daily_scheduler/config",
            data={"model": ""},
        )
        snapshot = client.app.state.registry.get("daily_scheduler").build_snapshot()

    saved_text = settings_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "model: null" in saved_text
    assert snapshot["model"] == "gpt-5"
    assert snapshot["model_source"] == "default"


def test_job_finder_page_is_removed(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/agents/job_finder")

    assert response.status_code == 404


def test_legacy_provider_fields_fail_validation(tmp_path: Path, monkeypatch) -> None:
    settings_path = tmp_path / "settings.yaml"
    settings_path.write_text(
        """\
openai:
  base_url: https://api.openai.com/v1
  default_model: gpt-5
agents:
  daily_scheduler:
    provider: openai
    model: gpt-5
    api_key_env_var: OPENAI_API_KEY
    daily_scheduler:
      reminder_cron: "0 * * * *"
      reset_cron: "0 0 * * *"
      workday_start: "09:00"
      focus_break_minutes: 10
      default_task_minutes: 45
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_AGENT_TOOL_SETTINGS_PATH", str(settings_path))
    with pytest.raises(ConfigError) as exc_info:
        load_settings()

    message = str(exc_info.value)
    assert "Settings validation failed" in message
    assert "provider" in message


def test_stream_starts_with_status_event(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        with client.stream("GET", "/stream/daily_scheduler") as response:
            first_chunk = next(response.iter_text())

    assert response.status_code == 200
    assert "event: status" in first_chunk
    assert '"agent_name": "daily_scheduler"' in first_chunk


def test_daily_schedule_page_renders_controls_and_empty_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/agents/daily_scheduler")

    assert response.status_code == 200
    assert "Schedule settings" in response.text
    assert "Start the day from the chat panel." in response.text


def test_daily_schedule_chat_creates_timeline(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "Review PRs, Implement scheduler API 90m"},
        )
        tasks = client.app.state.registry.get("daily_scheduler").repository.list_tasks()

    assert response.status_code == 200
    assert "Parsed 2 tasks" in response.text
    assert [task.title for task in tasks] == ["Review PRs", "Implement scheduler API"]


def test_daily_schedule_progress_update_reschedules_remaining_tasks(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "Review PRs, Implement scheduler API 90m"},
        )
        agent = client.app.state.registry.get("daily_scheduler")
        before = agent.repository.list_tasks()[1].start_time
        response = client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "done: Review PRs"},
        )
        tasks = agent.repository.list_tasks()

    assert response.status_code == 200
    assert "Rescheduled 1 remaining task" in response.text
    assert tasks[0].status == "done"
    assert tasks[1].start_time != before


def test_daily_schedule_overdue_branch_requires_decision(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "Review PRs, Implement scheduler API 90m"},
        )
        agent = client.app.state.registry.get("daily_scheduler")
        tasks = agent.repository.list_tasks()
        now = datetime.now().astimezone()
        tasks[0].start_time = (now - timedelta(minutes=90)).isoformat()
        tasks[0].end_time = (now - timedelta(minutes=15)).isoformat()
        agent.repository.save_tasks(tasks)

        response = client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "working on: Implement scheduler API"},
        )
        follow_up = client.post(
            "/agents/daily_scheduler/chat",
            data={"message": "keep"},
        )

    assert response.status_code == 200
    assert "is overdue" in response.text
    assert follow_up.status_code == 200
    assert "rebuilt the day plan" in follow_up.text


def test_daily_schedule_settings_reject_invalid_cron(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, settings_path, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/daily_scheduler/settings",
            data={
                "reminder_cron": "0 * * *",
                "reset_cron": "0 0 * * *",
                "workday_start": "09:00",
                "focus_break_minutes": "10",
                "default_task_minutes": "45",
            },
        )

    assert response.status_code == 422
    assert "5-field crontab" in response.text
    assert 'reminder_cron: "0 * * * *"' in settings_path.read_text(encoding="utf-8")


def test_crypto_airdrop_page_renders_controls_and_empty_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/agents/crypto_airdrop")

    assert response.status_code == 200
    assert "Radar configuration" in response.text
    assert "No ranked airdrops are stored for the latest cycle." in response.text


def test_crypto_airdrop_run_renders_ranked_cards(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post("/agents/crypto_airdrop/run")

    assert response.status_code == 200
    assert "LayerSpring Campaign" in response.text
    assert "Airdrops Io" in response.text
    assert "Crawl finished" in response.text


def test_crypto_airdrop_chat_filters_latest_cycle(tmp_path: Path, monkeypatch) -> None:
    client, _, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post("/agents/crypto_airdrop/run")
        response = client.post(
            "/agents/crypto_airdrop/chat",
            data={"message": "show only Ethereum airdrops"},
        )

    assert response.status_code == 200
    assert "filtered by chain ethereum" in response.text.lower()


def test_crypto_airdrop_settings_reject_invalid_cron(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, settings_path, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/crypto_airdrop/settings",
            data={
                "cron": "0 */6 * *",
                "airdrops_io_enabled": "on",
                "cryptorank_enabled": "on",
                "defillama_enabled": "on",
            },
        )

    assert response.status_code == 422
    assert "5-field crontab" in response.text
    assert 'cron: "0 */6 * * *"' in settings_path.read_text(encoding="utf-8")
