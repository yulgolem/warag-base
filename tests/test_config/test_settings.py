import os
from src.config.settings import Settings


def test_default_settings():
    settings = Settings()
    assert settings.postgres_dsn.startswith("postgresql://")
    assert settings.neo4j_uri.startswith("bolt://")
    assert settings.ollama_url.startswith("http://")
    assert settings.chunk_size == 500
    assert settings.chunk_overlap == 100
    assert settings.ui_port == 8501


def test_env_override(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db:5432/app")
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j:7687")
    monkeypatch.setenv("UI_PORT", "8600")
    settings = Settings()
    assert settings.postgres_dsn == "postgresql://user:pass@db:5432/app"
    assert settings.neo4j_uri == "bolt://neo4j:7687"
    assert settings.ui_port == 8600
