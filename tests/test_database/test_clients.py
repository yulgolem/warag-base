from src.database.postgres_client import PostgresClient
from src.database.neo4j_client import Neo4jClient


def test_postgres_client_init():
    client = PostgresClient(dsn="postgresql://example")
    assert client.dsn == "postgresql://example"


def test_neo4j_client_init():
    client = Neo4jClient(uri="bolt://example", user="u", password="p")
    assert client.uri == "bolt://example"
    assert client.user == "u"
    assert client.password == "p"
