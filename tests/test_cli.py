import yaml

from importlib import resources

import pytest


from writeragents.cli import main


def test_default_config_loading():
    config, db_mem, redis_mem = main([])
    text = resources.files("writeragents").joinpath("config/local.yaml").read_text()
    expected = yaml.safe_load(text)

    assert config == expected
    assert db_mem.url == expected['storage']['database_url']
    assert redis_mem.host == expected['storage']['redis_host']


def test_env_overrides(monkeypatch, tmp_path):
    cfg = tmp_path / "temp.yaml"
    cfg.write_text(
        "storage:\n  database_url: sqlite:///memory.db\n  redis_host: localhost\n"
    )
    monkeypatch.setenv("WRITERAG_CONFIG", str(cfg))
    monkeypatch.setenv("DATABASE_URL", "sqlite:///override.db")
    monkeypatch.setenv("REDIS_HOST", "overridehost")
    config, db_mem, redis_mem = main([])

    loaded = yaml.safe_load(cfg.read_text())
    assert config == loaded
    assert db_mem.url == "sqlite:///override.db"
    assert redis_mem.host == "overridehost"


def test_missing_config_path(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        main(["--config", str(missing)])


def test_invalid_config(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("foo: [")
    with pytest.raises(yaml.YAMLError):
        main(["--config", str(bad)])
