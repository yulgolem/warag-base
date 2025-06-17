import os
import shutil
from pathlib import Path
import pytest
from src.config.settings import Settings


@pytest.fixture(autouse=True)
def copy_env_file(tmp_path):
    """Ensure .env exists by copying from .env.example."""
    src = Path(".env.example")
    dst = Path(".env")
    if src.exists():
        shutil.copy(src, dst)
    yield
    if dst.exists():
        dst.unlink()


def test_settings_load_from_env():
    settings = Settings()
    assert settings.database.host == "postgres"
    assert settings.database.port == 5432
    assert settings.neo4j.uri == "bolt://neo4j:7687"
    assert settings.ollama.base_url == "http://ollama:11434"
    assert settings.chunking.chunk_size == 500
    assert settings.ui.port == 8501


def test_settings_override(monkeypatch):
    monkeypatch.setenv("DATABASE__HOST", "db.example")
    monkeypatch.setenv("UI__PORT", "8601")
    settings = Settings()
    assert settings.database.host == "db.example"
    assert settings.ui.port == 8601
