"""SQLite persistence for Daily Schedule tasks and messages."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from backend.agents.daily_scheduler.models import ChatMessage, TaskRecord


class DailyScheduleRepository:
    """Encapsulates SQLite reads and writes for schedule state."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path

    def initialize(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    estimated_minutes INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sort_order INTEGER NOT NULL,
                    created_at TEXT NOT NULL
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
                """
                CREATE TABLE IF NOT EXISTS scheduler_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_sort_order ON tasks(sort_order ASC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC)"
            )
            connection.commit()

    def replace_tasks(self, tasks: list[TaskRecord]) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM tasks")
            connection.executemany(
                """
                INSERT INTO tasks(
                    title, estimated_minutes, start_time, end_time,
                    status, sort_order, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        task.title,
                        task.estimated_minutes,
                        task.start_time,
                        task.end_time,
                        task.status,
                        task.sort_order,
                        task.created_at,
                    )
                    for task in tasks
                ],
            )
            connection.commit()

    def save_tasks(self, tasks: list[TaskRecord]) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM tasks")
            connection.executemany(
                """
                INSERT INTO tasks(
                    id, title, estimated_minutes, start_time, end_time,
                    status, sort_order, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        task.id,
                        task.title,
                        task.estimated_minutes,
                        task.start_time,
                        task.end_time,
                        task.status,
                        task.sort_order,
                        task.created_at,
                    )
                    for task in tasks
                ],
            )
            connection.commit()

    def list_tasks(self) -> list[TaskRecord]:
        with sqlite3.connect(self.storage_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, title, estimated_minutes, start_time, end_time,
                       status, sort_order, created_at
                FROM tasks
                ORDER BY sort_order ASC, id ASC
                """
            ).fetchall()

        return [
            TaskRecord(
                id=row["id"],
                title=row["title"],
                estimated_minutes=row["estimated_minutes"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                status=row["status"],
                sort_order=row["sort_order"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def clear_tasks(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM tasks")
            connection.commit()

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

    def list_messages(self, limit: int = 16) -> list[ChatMessage]:
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
            ChatMessage(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
        messages.reverse()
        return messages

    def clear_messages(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM messages")
            connection.commit()

    def set_state(self, key: str, value: str | None) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            if value is None:
                connection.execute("DELETE FROM scheduler_state WHERE key = ?", (key,))
            else:
                connection.execute(
                    """
                    INSERT INTO scheduler_state(key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (key, value),
                )
            connection.commit()

    def get_state(self, key: str) -> str | None:
        with sqlite3.connect(self.storage_path) as connection:
            row = connection.execute(
                "SELECT value FROM scheduler_state WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        return str(row[0])

    def clear_day(self) -> None:
        with sqlite3.connect(self.storage_path) as connection:
            connection.execute("DELETE FROM tasks")
            connection.execute("DELETE FROM messages")
            connection.execute("DELETE FROM scheduler_state")
            connection.commit()

