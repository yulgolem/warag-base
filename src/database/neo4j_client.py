from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from neo4j import GraphDatabase

from src.config.settings import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j driver wrapper with basic session handling."""

    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None):
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self._driver = None

    def connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver

    @contextmanager
    def session(self) -> Iterator:
        driver = self.connect()
        session = driver.session()
        try:
            yield session
        except Exception as exc:
            logger.error("Neo4j operation failed: %s", exc)
            raise
        finally:
            session.close()
