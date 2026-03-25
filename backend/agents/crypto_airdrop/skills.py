"""Deterministic analysis and filter helpers for the Crypto Airdrop agent."""

from __future__ import annotations

from datetime import date

from backend.agents.crypto_airdrop.models import AirdropRecord


def score_airdrop(airdrop: AirdropRecord) -> int:
    """Compute a deterministic score for one airdrop record."""

    score = 38
    score += _signal_score(airdrop.team_signal, high=18, medium=10)
    score += _signal_score(airdrop.tokenomics_signal, high=16, medium=8)
    score += _signal_score(airdrop.community_signal, high=14, medium=7)
    score += _signal_score(airdrop.task_reward_signal, high=12, medium=6)

    if airdrop.chain.lower() in {"ethereum", "solana", "base", "arbitrum"}:
        score += 6

    if airdrop.deadline:
        try:
            days_left = (date.fromisoformat(airdrop.deadline) - date.today()).days
        except ValueError:
            days_left = 30
        if days_left <= 7:
            score -= 4
        elif days_left >= 21:
            score += 4

    return max(0, min(score, 100))


def build_reason(airdrop: AirdropRecord) -> str:
    """Generate a deterministic ranking explanation."""

    reasons = [
        f"Team signal is {airdrop.team_signal}.",
        f"Tokenomics signal is {airdrop.tokenomics_signal}.",
        f"Community signal is {airdrop.community_signal}.",
        f"Task-versus-reward signal is {airdrop.task_reward_signal}.",
    ]
    if airdrop.deadline:
        reasons.append(f"Deadline tracked for {airdrop.deadline}.")
    return " ".join(reasons)


def filter_airdrops(
    airdrops: list[AirdropRecord],
    message: str,
) -> tuple[list[AirdropRecord], str]:
    """Filter current airdrops by source, chain, or free-text keywords."""

    normalized = message.strip().lower()
    if not normalized:
        return airdrops, "Showing the current ranked airdrop list."

    if "all" in normalized and "airdrop" in normalized:
        return airdrops, f"Showing all {len(airdrops)} ranked airdrops."

    source_terms = {
        "airdrops_io": "airdrops.io",
        "cryptorank": "cryptorank",
        "defillama": "defillama",
    }
    chain_terms = {airdrop.chain.lower() for airdrop in airdrops}

    matched_sources = [
        source_name
        for source_name, label in source_terms.items()
        if label in normalized or source_name in normalized
    ]
    matched_chains = [chain for chain in chain_terms if chain in normalized]

    filtered = airdrops
    if matched_sources:
        allowed_sources = set(matched_sources)
        filtered = [airdrop for airdrop in filtered if airdrop.source in allowed_sources]
    if matched_chains:
        allowed_chains = set(matched_chains)
        filtered = [
            airdrop for airdrop in filtered if airdrop.chain.lower() in allowed_chains
        ]

    if matched_sources or matched_chains:
        descriptors: list[str] = []
        if matched_chains:
            descriptors.append(f"chain {', '.join(sorted(matched_chains))}")
        if matched_sources:
            labels = [source_terms[source] for source in matched_sources]
            descriptors.append(f"source {', '.join(labels)}")
        return (
            filtered,
            f"Showing {len(filtered)} airdrops filtered by {' and '.join(descriptors)}.",
        )

    tokens = [token for token in normalized.replace("show", "").split() if len(token) > 2]
    if not tokens:
        return airdrops, "Try filtering by chain, source, or a keyword from the card summaries."

    filtered = [
        airdrop
        for airdrop in airdrops
        if any(
            token in " ".join(
                [
                    airdrop.name,
                    airdrop.chain,
                    airdrop.requirements_summary,
                    airdrop.source.replace("_", " "),
                ]
            ).lower()
            for token in tokens
        )
    ]
    if not filtered:
        return [], "No stored airdrops matched that filter yet."

    return filtered, f"Showing {len(filtered)} airdrops matching `{message.strip()}`."


def _signal_score(signal: str, *, high: int, medium: int) -> int:
    lowered = signal.lower()
    if lowered == "high":
        return high
    if lowered == "medium":
        return medium
    return 0

