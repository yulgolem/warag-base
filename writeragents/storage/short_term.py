"""Short-term memory using Redis."""

from __future__ import annotations

import redis


class RedisMemory:
    """Simple wrapper around a Redis client."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.client = redis.Redis(host=host, port=port, db=db)

    # ------------------------------------------------------------------
    def get(self, key: str) -> str | None:
        """Return the value for ``key`` if present."""
        val = self.client.get(key)
        if val is not None and not isinstance(val, str):
            val = val.decode("utf-8")
        return val

    def set(self, key: str, value: str) -> None:
        """Store ``value`` under ``key``."""
        self.client.set(key, value)
