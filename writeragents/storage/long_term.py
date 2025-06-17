"""Long-term memory using SQLite or PostgreSQL."""

from __future__ import annotations

import sqlite3
from typing import Any

import psycopg2


class DatabaseMemory:
    """Persist chat history or other long-lived data."""

    def __init__(self, url: str = "sqlite:///memory.db") -> None:
        self.url = url
        if url.startswith("sqlite:///"):
            path = url.split("sqlite:///")[1]
            self.conn: Any = sqlite3.connect(path)
            self.placeholder = "?"
        else:
            self.conn = psycopg2.connect(url)
            self.placeholder = "%s"
        self._ensure_table()

    # ------------------------------------------------------------------
    def _ensure_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            (
                "CREATE TABLE IF NOT EXISTS memory ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "data TEXT)"
            )
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    def fetch(self, query: str, *params: Any) -> list[tuple]:
        """Return rows matching ``query``."""
        cur = self.conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return rows

    def store(self, data: str) -> None:
        """Persist a simple text record."""
        cur = self.conn.cursor()
        cur.execute(
            f"INSERT INTO memory (data) VALUES ({self.placeholder})",
            (data,),
        )
        self.conn.commit()
