import types
import pytest

from src.database.postgres_client import PostgresClient
from src.database.neo4j_client import Neo4jClient


class DummyPool:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.closed = False

    def getconn(self):
        return object()

    def putconn(self, conn, close=False):
        pass

    def closeall(self):
        self.closed = True


class DummyDriver:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.closed = False

    def session(self):
        class DummySession:
            def execute_read(self, fn):
                return fn(types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(data=lambda: [1])))

            def execute_write(self, fn):
                return fn(types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(data=lambda: [1])))

            def close(self):
                pass
        return DummySession()

    def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    monkeypatch.setattr('psycopg2.pool.SimpleConnectionPool', DummyPool)
    monkeypatch.setattr('pgvector.psycopg2.register_vector', lambda conn: None)
    monkeypatch.setattr('neo4j.GraphDatabase.driver', lambda *a, **k: DummyDriver(*a, **k))


def test_postgres_client_connect():
    client = PostgresClient('h', 1, 'db', 'u', 'p')
    assert isinstance(client.pool, DummyPool)


def test_postgres_client_health_check(monkeypatch):
    client = PostgresClient('h', 1, 'db', 'u', 'p')
    monkeypatch.setattr(client, 'execute', lambda *a, **k: [1])
    assert client.health_check() is True


def test_neo4j_client_connect():
    client = Neo4jClient('bolt://n', 'u', 'p')
    assert isinstance(client.driver, DummyDriver)


def test_neo4j_client_health_check(monkeypatch):
    client = Neo4jClient('bolt://n', 'u', 'p')
    monkeypatch.setattr(client, 'execute', lambda *a, **k: [1])
    assert client.health_check() is True
