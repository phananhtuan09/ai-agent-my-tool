"""Fixture-backed source adapters for the Crypto Airdrop agent."""

from __future__ import annotations

from backend.agents.crypto_airdrop.models import AirdropRecord


def get_fixture_airdrops(source: str) -> list[AirdropRecord]:
    """Return deterministic fixture rows for one configured source."""

    fixtures: dict[str, list[AirdropRecord]] = {
        "airdrops_io": [
            AirdropRecord(
                name="LayerSpring Campaign",
                chain="Ethereum",
                requirements_summary="Bridge funds, mint an NFT badge, and complete 3 social quests.",
                source="airdrops_io",
                source_url="https://airdrops.io/layerspring/",
                deadline="2026-04-15",
                team_signal="high",
                tokenomics_signal="medium",
                community_signal="high",
                task_reward_signal="medium",
            ),
            AirdropRecord(
                name="Orbit Mint Sprint",
                chain="Base",
                requirements_summary="Swap on partner dApps and keep two weekly check-ins active.",
                source="airdrops_io",
                source_url="https://airdrops.io/orbit-mint/",
                deadline="2026-04-08",
                team_signal="medium",
                tokenomics_signal="medium",
                community_signal="medium",
                task_reward_signal="high",
            ),
        ],
        "cryptorank": [
            AirdropRecord(
                name="SolForge XP",
                chain="Solana",
                requirements_summary="Trade once, stake points, and invite two wallets.",
                source="cryptorank",
                source_url="https://cryptorank.io/drophunting/solforge-activity",
                deadline="2026-04-20",
                team_signal="medium",
                tokenomics_signal="high",
                community_signal="high",
                task_reward_signal="high",
            ),
            AirdropRecord(
                name="Arbitrum Atlas",
                chain="Arbitrum",
                requirements_summary="Bridge, vote on governance topics, and complete onchain quests.",
                source="cryptorank",
                source_url="https://cryptorank.io/drophunting/arbitrum-atlas-activity",
                deadline="2026-04-03",
                team_signal="high",
                tokenomics_signal="medium",
                community_signal="medium",
                task_reward_signal="medium",
            ),
        ],
        "defillama": [
            AirdropRecord(
                name="Llama Loop",
                chain="Cosmos",
                requirements_summary="Provide liquidity and maintain weekly active usage for four epochs.",
                source="defillama",
                source_url="https://defillama.com/airdrops/llama-loop",
                deadline="2026-05-01",
                team_signal="high",
                tokenomics_signal="high",
                community_signal="medium",
                task_reward_signal="medium",
            ),
            AirdropRecord(
                name="Mode Questboard",
                chain="Ethereum",
                requirements_summary="Connect a wallet, finish ecosystem quests, and hold a campaign role.",
                source="defillama",
                source_url="https://defillama.com/airdrops/mode-questboard",
                deadline="2026-04-11",
                team_signal="medium",
                tokenomics_signal="medium",
                community_signal="high",
                task_reward_signal="medium",
            ),
        ],
    }
    return [
        AirdropRecord(
            name=record.name,
            chain=record.chain,
            requirements_summary=record.requirements_summary,
            source=record.source,
            source_url=record.source_url,
            deadline=record.deadline,
            team_signal=record.team_signal,
            tokenomics_signal=record.tokenomics_signal,
            community_signal=record.community_signal,
            task_reward_signal=record.task_reward_signal,
        )
        for record in fixtures.get(source, [])
    ]
