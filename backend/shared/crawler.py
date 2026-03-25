"""Shared crawl serialization helpers."""

from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import TypeVar


T = TypeVar("T")

_CRAWL_LOCK = Lock()


def run_serialized(executor: Callable[[], T]) -> T:
    """Run one crawl workload at a time across the process."""

    with _CRAWL_LOCK:
        return executor()
