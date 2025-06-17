from __future__ import annotations

from typing import Any, Optional

import pgvector.psycopg2  # type: ignore
import psycopg2
from psycopg2 import pool


class PostgresClient:
    """PostgreSQL client with pgvector support and connection pooling."""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        minconn: int = 1,
        maxconn: int = 5,
    ) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.minconn = minconn
        self.maxconn = maxconn
        self.pool: Optional[pool.SimpleConnectionPool] = None
        self.connect()

    def connect(self) -> None:
        """Initialize connection pool and register pgvector."""
        self.pool = pool.SimpleConnectionPool(
            self.minconn,
            self.maxconn,
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
        )
        conn = self.pool.getconn()
        try:
            pgvector.psycopg2.register_vector(conn)
        finally:
            self.pool.putconn(conn)

    def close(self) -> None:
        if self.pool:
            self.pool.closeall()
            self.pool = None

    def reconnect(self) -> None:
        self.close()
        self.connect()

    def execute(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[Any]:
        """Execute a query with basic reconnection logic."""
        attempts = 2
        last_error: Optional[Exception] = None
        for _ in range(attempts):
            conn = None
            try:
                if not self.pool:
                    self.connect()
                conn = self.pool.getconn()  # type: ignore[assignment]
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    result = cur.fetchall() if cur.description else []
                    conn.commit()
                self.pool.putconn(conn)
                return result
            except Exception as e:  # pragma: no cover - connection errors
                last_error = e
                if conn is not None and self.pool:
                    self.pool.putconn(conn, close=True)
                self.reconnect()
        if last_error:
            raise last_error
        return []

    def health_check(self) -> bool:
        """Run a simple health check query."""
        try:
            self.execute("SELECT 1;")
            return True
        except Exception:
            return False
