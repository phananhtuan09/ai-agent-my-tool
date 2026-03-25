from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import create_app


TEST_SETTINGS = """\
agents:
  job_finder:
    provider: anthropic
    model: claude-3-7-sonnet-latest
    api_key_env_var: ANTHROPIC_API_KEY
    job_finder:
      cron: "0 8 * * *"
      sources:
        topcv:
          enabled: true
          label: TopCV
        itviec:
          enabled: true
          label: ITviec
        vietnamworks:
          enabled: true
          label: VietnamWorks
      filters:
        salary_min: 1500
        salary_max: 3000
        locations:
          - Ho Chi Minh City
        must_have_frameworks:
          - React
        nice_to_have_frameworks:
          - Next.js
        exclude_keywords:
          - intern
  daily_scheduler:
    provider: openai
    model: gpt-5-mini
    api_key_env_var: OPENAI_API_KEY
    daily_scheduler:
      reminder_cron: "0 * * * *"
      reset_cron: "0 0 * * *"
      workday_start: "09:00"
      focus_break_minutes: 10
      default_task_minutes: 45
  crypto_airdrop:
    provider: openai
    model: gpt-5
    api_key_env_var: OPENAI_API_KEY
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


def _build_client(tmp_path: Path, monkeypatch) -> tuple[TestClient, Path]:
    settings_path = tmp_path / "settings.yaml"
    settings_path.write_text(TEST_SETTINGS, encoding="utf-8")
    monkeypatch.setenv("AI_AGENT_TOOL_SETTINGS_PATH", str(settings_path))
    return TestClient(create_app()), settings_path


def test_dashboard_lists_registered_agents(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Job Finder" in response.text
    assert "Daily Schedule" in response.text
    assert "Crypto Airdrop" in response.text


def test_config_update_persists_and_hot_swaps(tmp_path: Path, monkeypatch) -> None:
    client, settings_path = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/job_finder/config",
            data={
                "provider": "openai",
                "model": "gpt-5-mini",
                "api_key_env_var": "OPENAI_API_KEY",
            },
        )
        snapshot = client.app.state.registry.get("job_finder").build_snapshot()

    saved_text = settings_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "Configuration saved" in response.text
    assert "provider: openai" in saved_text
    assert snapshot["provider"] == "openai"
    assert snapshot["model"] == "gpt-5-mini"


def test_stream_starts_with_status_event(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        with client.stream("GET", "/stream/job_finder") as response:
            first_chunk = next(response.iter_text())

    assert response.status_code == 200
    assert "event: status" in first_chunk
    assert '"agent_name": "job_finder"' in first_chunk


def test_job_filter_update_persists_nested_settings(tmp_path: Path, monkeypatch) -> None:
    client, settings_path = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/job_finder/filters",
            data={
                "salary_min": "1800",
                "salary_max": "2800",
                "locations": "Ho Chi Minh City, Hanoi",
                "must_have_frameworks": "React, TypeScript",
                "nice_to_have_frameworks": "Next.js",
                "exclude_keywords": "intern",
                "cron": "15 8 * * *",
                "topcv_enabled": "on",
                "itviec_enabled": "on",
                "vietnamworks_enabled": "on",
            },
        )

    saved_text = settings_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "Job filter settings saved" in response.text
    assert 'cron: 15 8 * * *' in saved_text
    assert "- TypeScript" in saved_text


def test_job_run_renders_ranked_cards(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post("/agents/job_finder/run")

    assert response.status_code == 200
    assert "Senior React Engineer" in response.text
    assert "Open source listing" in response.text
    assert "Crawl finished" in response.text
    assert "Deterministic fallback used" in response.text


def test_job_run_shows_empty_state_when_filters_exclude_everything(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post(
            "/agents/job_finder/filters",
            data={
                "salary_min": "9000",
                "salary_max": "12000",
                "locations": "Tokyo",
                "must_have_frameworks": "Elixir",
                "nice_to_have_frameworks": "",
                "exclude_keywords": "",
                "cron": "0 8 * * *",
                "topcv_enabled": "on",
                "itviec_enabled": "on",
                "vietnamworks_enabled": "on",
            },
        )
        response = client.post("/agents/job_finder/run")

    assert response.status_code == 200
    assert "No jobs passed the hard filters yet" in response.text


def test_job_run_rejects_when_all_sources_disabled(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        client.post(
            "/agents/job_finder/filters",
            data={
                "salary_min": "1500",
                "salary_max": "3000",
                "locations": "Ho Chi Minh City",
                "must_have_frameworks": "React",
                "nice_to_have_frameworks": "Next.js",
                "exclude_keywords": "intern",
                "cron": "0 8 * * *",
            },
        )
        response = client.post("/agents/job_finder/run")

    assert response.status_code == 422
    assert "Enable at least one job source" in response.text


def test_job_run_shows_partial_failure_warning(tmp_path: Path, monkeypatch) -> None:
    client, settings_path = _build_client(tmp_path, monkeypatch)
    settings_path.write_text(
        TEST_SETTINGS.replace("label: ITviec", "label: ITviec\n          simulate_failure: true"),
        encoding="utf-8",
    )

    with client:
        response = client.post("/agents/job_finder/run")

    assert response.status_code == 200
    assert "itviec crawl failed; other sources continued" in response.text
    assert "Senior React Engineer" in response.text


def test_job_filter_rejects_invalid_cron(tmp_path: Path, monkeypatch) -> None:
    client, settings_path = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post(
            "/agents/job_finder/filters",
            data={
                "salary_min": "1500",
                "salary_max": "3000",
                "locations": "Ho Chi Minh City",
                "must_have_frameworks": "React",
                "nice_to_have_frameworks": "Next.js",
                "exclude_keywords": "intern",
                "cron": "0 8 * *",
                "topcv_enabled": "on",
                "itviec_enabled": "on",
                "vietnamworks_enabled": "on",
            },
        )

    saved_text = settings_path.read_text(encoding="utf-8")

    assert response.status_code == 422
    assert "5-field crontab" in response.text
    assert 'cron: "0 8 * * *"' in saved_text


def test_job_filter_returns_400_for_malformed_yaml(tmp_path: Path, monkeypatch) -> None:
    client, settings_path = _build_client(tmp_path, monkeypatch)

    with client:
        settings_path.write_text("agents: [broken", encoding="utf-8")
        response = client.post(
            "/agents/job_finder/filters",
            data={
                "salary_min": "1500",
                "salary_max": "3000",
                "locations": "Ho Chi Minh City",
                "must_have_frameworks": "React",
                "nice_to_have_frameworks": "Next.js",
                "exclude_keywords": "intern",
                "cron": "0 8 * * *",
                "topcv_enabled": "on",
                "itviec_enabled": "on",
                "vietnamworks_enabled": "on",
            },
        )

    assert response.status_code == 400
    assert "Settings YAML is malformed" in response.text


def test_daily_schedule_page_renders_controls_and_empty_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/agents/daily_scheduler")

    assert response.status_code == 200
    assert "Schedule settings" in response.text
    assert "Start the day from the chat panel." in response.text


def test_daily_schedule_chat_creates_timeline(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

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
    client, _ = _build_client(tmp_path, monkeypatch)

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
    client, _ = _build_client(tmp_path, monkeypatch)

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
    client, settings_path = _build_client(tmp_path, monkeypatch)

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
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.get("/agents/crypto_airdrop")

    assert response.status_code == 200
    assert "Radar configuration" in response.text
    assert "No ranked airdrops are stored for the latest cycle." in response.text


def test_crypto_airdrop_run_renders_ranked_cards(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

    with client:
        response = client.post("/agents/crypto_airdrop/run")

    assert response.status_code == 200
    assert "LayerSpring Campaign" in response.text
    assert "Open source page" in response.text
    assert "Crawl finished" in response.text


def test_crypto_airdrop_chat_filters_latest_cycle(tmp_path: Path, monkeypatch) -> None:
    client, _ = _build_client(tmp_path, monkeypatch)

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
    client, settings_path = _build_client(tmp_path, monkeypatch)

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
