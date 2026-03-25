"""SQLite persistence for Crypto Airdrop cycles, results, and chat messages."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from backend.agents.crypto_airdrop.models import AirdropChatMessage, AirdropRecord


class CryptoAirdropRepository:
    """Encapsulates SQLite reads and writes for airdrop data."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path

    def initialize(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS crawl_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS airdrops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crawl_cycle_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    requirements_summary TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    deadline TEXT,
                    team_signal TEXT NOT NULL,
                    tokenomics_signal TEXT NOT NULL,
                    community_signal TEXT NOT NULL,
                    task_reward_signal TEXT NOT NULL,
                    ai_score INTEGER,
                    ai_reason TEXT,
                    crawled_at TEXT NOT NULL,
                    FOREIGN KEY(crawl_cycle_id) REFERENCES crawl_cycles(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_airdrops_cycle ON airdrops(crawl_cycle_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_airdrops_score ON airdrops(ai_score DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC)"
            )
            connection.commit()

    def start_cycle(self) -> int:
        with sqlite3.connect(self.storage_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO crawl_cycles(started_at)
                VALUES (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now'))
                """
            )
            connection.commit()
            return int(cursor.lastrowid)

    def complete_cycle(self, cycle_id: int) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute(
                """
                UPDATE crawl_cycles
                SET completed_at = strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')
                WHERE id = ?
                """,
                (cycle_id,),
            )
            connection.commit()

    def replace_cycle_airdrops(self, cycle_id: int, airdrops: list[AirdropRecord]) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM airdrops WHERE crawl_cycle_id = ?", (cycle_id,))
            connection.executemany(
                """
                INSERT INTO airdrops(
                    crawl_cycle_id, name, chain, requirements_summary, source, source_url,
                    deadline, team_signal, tokenomics_signal, community_signal,
                    task_reward_signal, ai_score, ai_reason, crawled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        cycle_id,
                        airdrop.name,
                        airdrop.chain,
                        airdrop.requirements_summary,
                        airdrop.source,
                        airdrop.source_url,
                        airdrop.deadline,
                        airdrop.team_signal,
                        airdrop.tokenomics_signal,
                        airdrop.community_signal,
                        airdrop.task_reward_signal,
                        airdrop.ai_score,
                        airdrop.ai_reason,
                        airdrop.crawled_at,
                    )
                    for airdrop in airdrops
                ],
            )
            connection.commit()

    def purge_old_cycles(self, retain_count: int = 10) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            rows = connection.execute(
                """
                SELECT id
                FROM crawl_cycles
                ORDER BY id DESC
                LIMIT -1 OFFSET ?
                """,
                (retain_count,),
            ).fetchall()
            cycle_ids = [row[0] for row in rows]
            if cycle_ids:
                placeholders = ", ".join("?" for _ in cycle_ids)
                connection.execute(
                    f"DELETE FROM airdrops WHERE crawl_cycle_id IN ({placeholders})",
                    cycle_ids,
                )
                connection.execute(
                    f"DELETE FROM crawl_cycles WHERE id IN ({placeholders})",
                    cycle_ids,
                )
            connection.commit()

    def list_latest_airdrops(self, limit: int = 24) -> list[AirdropRecord]:
        cycle_id = self.get_latest_cycle_id()
        if cycle_id is None:
            return []
        with sqlite3.connect(self.storage_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT crawl_cycle_id, name, chain, requirements_summary, source, source_url,
                       deadline, team_signal, tokenomics_signal, community_signal,
                       task_reward_signal, ai_score, ai_reason, crawled_at
                FROM airdrops
                WHERE crawl_cycle_id = ?
                ORDER BY ai_score DESC, name ASC
                LIMIT ?
                """,
                (cycle_id, limit),
            ).fetchall()
        return [self._row_to_airdrop(row) for row in rows]

    def get_latest_cycle_id(self) -> int | None:
        with sqlite3.connect(self.storage_path) as connection:
            row = connection.execute(
                "SELECT id FROM crawl_cycles ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        return int(row[0])

    def append_message(self, role: str, content: str) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute(
                """
                INSERT INTO messages(role, content, created_at)
                VALUES (?, ?, strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now'))
                """,
                (role, content),
            )
            connection.commit()

    def list_messages(self, limit: int = 16) -> list[AirdropChatMessage]:
        with sqlite3.connect(self.storage_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, role, content, created_at
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        messages = [
            AirdropChatMessage(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
        messages.reverse()
        return messages

    def _row_to_airdrop(self, row: sqlite3.Row) -> AirdropRecord:
        return AirdropRecord(
            crawl_cycle_id=row["crawl_cycle_id"],
            name=row["name"],
            chain=row["chain"],
            requirements_summary=row["requirements_summary"],
            source=row["source"],
            source_url=row["source_url"],
            deadline=row["deadline"],
            team_signal=row["team_signal"],
            tokenomics_signal=row["tokenomics_signal"],
            community_signal=row["community_signal"],
            task_reward_signal=row["task_reward_signal"],
            ai_score=row["ai_score"],
            ai_reason=row["ai_reason"],
            crawled_at=row["crawled_at"],
        )

