import os
import shutil



def test_default_settings(tmp_path):
    env_path = tmp_path / ".env"
    shutil.copyfile(".env.example", env_path)
    os.environ["ENV_FILE"] = str(env_path)
    import importlib
    import src.config.settings as settings_module
    importlib.reload(settings_module)
    settings = settings_module.Settings(_env_file=env_path)
    assert settings.postgres_dsn.startswith("postgresql://")
    assert settings.neo4j_uri.startswith("bolt://")
    assert settings.ollama_url.startswith("http://")
    assert settings.chunk_size == 500
    assert settings.chunk_overlap == 100
    assert settings.ui_port == 8501


def test_env_override(monkeypatch, tmp_path):
    env_path = tmp_path / ".env"
    shutil.copyfile(".env.example", env_path)
    os.environ["ENV_FILE"] = str(env_path)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db:5432/app")
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j:7687")
    monkeypatch.setenv("UI_PORT", "8600")
    import importlib
    import src.config.settings as settings_module
    importlib.reload(settings_module)
    settings = settings_module.Settings(_env_file=env_path)
    assert settings.postgres_dsn == "postgresql://user:pass@db:5432/app"
    assert settings.neo4j_uri == "bolt://neo4j:7687"
    assert settings.ui_port == 8600
