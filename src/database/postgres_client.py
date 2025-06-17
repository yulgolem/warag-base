from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extras import RealDictCursor

from src.config.settings import settings

logger = logging.getLogger(__name__)


class PostgresClient:
    """Simple PostgreSQL client with connection pooling."""

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or settings.postgres_dsn
        self._pool = None

    def connect(self):
        if self._pool is None:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                1, 5, dsn=self.dsn, cursor_factory=RealDictCursor
            )
        return self._pool

    @contextmanager
    def session(self) -> Iterator[psycopg2.extensions.connection]:
        pool = self.connect()
        conn = pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error("PostgreSQL operation failed: %s", exc)
            raise
        finally:
            pool.putconn(conn)
