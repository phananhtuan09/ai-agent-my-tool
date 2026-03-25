"""Crawl, score, and filter pipeline for the Crypto Airdrop agent."""

from __future__ import annotations

from backend.agents.crypto_airdrop.models import AirdropRecord, AirdropRunSummary
from backend.agents.crypto_airdrop.sources import fetch_source_airdrops
from backend.agents.crypto_airdrop.skills import build_reason, filter_airdrops, score_airdrop
from backend.exceptions import ConfigError, CrawlError
from backend.shared.crawler import run_serialized
from backend.shared.llm_client import LLMClient
from backend.shared.settings import CryptoAirdropRuntimeSettings


def run_airdrop_pipeline(
    runtime_settings: CryptoAirdropRuntimeSettings,
    llm_client: LLMClient,
    trigger: str,
) -> AirdropRunSummary:
    """Run crawl and ranking for one airdrop execution."""

    enabled_sources = {
        name: config
        for name, config in runtime_settings.sources.items()
        if config.enabled
    }
    if not enabled_sources:
        raise ConfigError("Enable at least one airdrop source before running a crawl.")

    warnings: list[str] = []

    def crawl_all() -> list[AirdropRecord]:
        records: list[AirdropRecord] = []
        for source_name, source_config in enabled_sources.items():
            try:
                crawled_records, warning = _crawl_source(
                    source_name,
                    source_config.simulate_failure,
                )
                records.extend(crawled_records)
                if warning:
                    warnings.append(warning)
            except CrawlError as exc:
                warnings.append(str(exc))
        return records

    crawled_records = run_serialized(crawl_all)
    ranked_records = rank_airdrops(crawled_records, llm_client)

    return AirdropRunSummary(
        airdrops=ranked_records,
        warnings=warnings,
        matched_count=len(ranked_records),
        crawled_count=len(crawled_records),
        trigger=trigger,
    )


def rank_airdrops(
    airdrops: list[AirdropRecord],
    llm_client: LLMClient,
) -> list[AirdropRecord]:
    """Rank airdrops with a deterministic fallback that remains usable offline."""

    ranked: list[AirdropRecord] = []
    for airdrop in airdrops:
        airdrop.ai_score = score_airdrop(airdrop)
        airdrop.ai_reason = build_reason(airdrop)
        if not llm_client.is_configured:
            airdrop.ai_reason = (
                f"{airdrop.ai_reason} Deterministic fallback used because "
                f"{llm_client.api_key_env_var} is not configured."
            )
        ranked.append(airdrop)
    return sorted(ranked, key=lambda item: (item.ai_score or 0, item.name), reverse=True)


def apply_chat_filter(
    airdrops: list[AirdropRecord],
    message: str,
) -> tuple[list[AirdropRecord], str]:
    """Apply a chat-driven filter to the latest ranked records."""

    return filter_airdrops(airdrops, message)


def _crawl_source(
    source_name: str,
    simulate_failure: bool,
) -> tuple[list[AirdropRecord], str | None]:
    if simulate_failure:
        raise CrawlError(f"{source_name} crawl failed; other sources continued.")
    return fetch_source_airdrops(source_name)
