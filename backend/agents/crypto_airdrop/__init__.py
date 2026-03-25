"""Crypto Airdrop agent package."""

from backend.agents._registry import AgentRegistry
from backend.agents.crypto_airdrop.agent import CryptoAirdropAgent


def register(registry: AgentRegistry) -> None:
    """Register the Crypto Airdrop agent with the shared registry."""

    registry.register(
        CryptoAirdropAgent(
            settings=registry.get_settings("crypto_airdrop"),
            broker=registry.broker,
        )
    )
