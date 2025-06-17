from __future__ import annotations

from typing import Any, Optional

from neo4j import GraphDatabase, basic_auth


class Neo4jClient:
    """Neo4j client with connection pooling and health check."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        max_pool_size: int = 10,
    ) -> None:
        self.uri = uri
        self.user = user
        self.password = password
        self.max_pool_size = max_pool_size
        self.driver: Optional[GraphDatabase.driver] = None
        self.connect()

    def connect(self) -> None:
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=basic_auth(self.user, self.password),
            max_connection_pool_size=self.max_pool_size,
        )

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            self.driver = None

    def reconnect(self) -> None:
        self.close()
        self.connect()

    def execute(
        self, cypher: str, parameters: Optional[dict[str, Any]] = None, readonly: bool = False
    ) -> list[Any]:
        attempts = 2
        last_error: Optional[Exception] = None
        for _ in range(attempts):
            session = None
            try:
                if not self.driver:
                    self.connect()
                session = self.driver.session()
                if readonly:
                    result = session.execute_read(lambda tx: tx.run(cypher, parameters).data())
                else:
                    result = session.execute_write(lambda tx: tx.run(cypher, parameters).data())
                session.close()
                return result
            except Exception as e:  # pragma: no cover - connection errors
                last_error = e
                if session is not None:
                    session.close()
                self.reconnect()
        if last_error:
            raise last_error
        return []

    def health_check(self) -> bool:
        try:
            self.execute("RETURN 1 AS result", readonly=True)
            return True
        except Exception:
            return False
