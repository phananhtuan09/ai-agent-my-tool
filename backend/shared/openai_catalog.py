"""Helpers for testing OpenAI-compatible connectivity and model discovery."""

from __future__ import annotations

from typing import Any

import httpx

from backend.exceptions import ConfigError


def _models_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/models"


async def fetch_openai_models(base_url: str, api_key: str) -> list[str]:
    """Fetch model identifiers from an OpenAI-compatible models endpoint."""

    request_url = _models_url(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(request_url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        raise ConfigError(
            f"Model fetch failed with HTTP {exc.response.status_code}: {detail}"
        ) from exc
    except httpx.HTTPError as exc:
        raise ConfigError(f"Model fetch failed: {exc}") from exc

    try:
        payload: dict[str, Any] = response.json()
    except ValueError as exc:
        raise ConfigError("Model fetch failed: response was not valid JSON.") from exc

    model_rows = payload.get("data")
    if not isinstance(model_rows, list):
        raise ConfigError("Model fetch failed: response did not include a model list.")

    discovered_models = sorted(
        {
            str(item.get("id", "")).strip()
            for item in model_rows
            if isinstance(item, dict) and str(item.get("id", "")).strip()
        },
        key=str.casefold,
    )
    if not discovered_models:
        raise ConfigError("Model fetch failed: no model ids were returned by the API.")

    return discovered_models
