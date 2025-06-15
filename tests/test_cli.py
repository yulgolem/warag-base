import yaml
from importlib import resources

from writeragents.cli import main


def test_default_config_loading():
    config, db_mem, redis_mem = main([])
    text = resources.files("writeragents").joinpath("config/local.yaml").read_text()
    expected = yaml.safe_load(text)

    assert called["text"] == "hello"
    assert config == expected
    assert db_mem.url == expected["storage"]["database_url"]
    assert redis_mem.host == expected["storage"]["redis_host"]


def test_write_command_dispatch(monkeypatch):
    called = {}

    def fake_run(self, prompt):
        called["prompt"] = prompt

    monkeypatch.setattr(WriterAgent, "run", fake_run)
    main(["write", "Begin"])
    assert called["prompt"] == "Begin"


def test_config_option_parsing(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "storage:\n  database_url: sqlite:///tmp.db\n  redis_host: otherhost\n"
    )

    called = {}

    def fake_run(self, prompt):
        called["prompt"] = prompt

    monkeypatch.setattr(WriterAgent, "run", fake_run)
    config, db_mem, redis_mem = main([
        "--config",
        str(cfg),
        "write",
        "Go",
    ])

    assert called["prompt"] == "Go"
    assert config["storage"]["database_url"] == "sqlite:///tmp.db"
    assert db_mem.url == "sqlite:///tmp.db"
    assert redis_mem.host == "otherhost"
