import yaml

import os
from pathlib import Path
from importlib import resources

import pytest

from writeragents.cli import main
from writeragents.agents.orchestrator.agent import Orchestrator
from writeragents.agents.wba.agent import WorldBuildingArchivist


def test_default_config_loading(monkeypatch):
    called = {}

    def fake_archive(self, text):
        called["text"] = text

    monkeypatch.setattr(WorldBuildingArchivist, "archive_text", fake_archive)
    config, db_mem, redis_mem = main(["archive", "hello"])
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

    monkeypatch.setattr(Orchestrator, "run", fake_run)
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

    monkeypatch.setattr(Orchestrator, "run", fake_run)
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


def test_candidate_limit_default(monkeypatch):
    called = {}

    def fake_init(
        self,
        store=None,
        candidate_limit=3,
        classification_threshold=0.8,
    ):
        called["limit"] = candidate_limit

    monkeypatch.setattr(WorldBuildingArchivist, "__init__", fake_init)
    monkeypatch.setattr(WorldBuildingArchivist, "archive_text", lambda self, t: None)
    main(["archive", "text"])
    assert called["limit"] == 3


def test_candidate_limit_from_config(tmp_path, monkeypatch):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("wba:\n  candidate_limit: 5\n")
    called = {}

    def fake_init(self, store=None, candidate_limit=3, classification_threshold=0.8):
        called["limit"] = candidate_limit

    monkeypatch.setattr(WorldBuildingArchivist, "__init__", fake_init)
    monkeypatch.setattr(WorldBuildingArchivist, "archive_text", lambda self, t: None)
    main(["--config", str(cfg), "archive", "text"])
    assert called["limit"] == 5


def test_threshold_default(monkeypatch):
    captured = {}

    def fake_init(
        self,
        store=None,
        candidate_limit=3,
        classification_threshold=0.8,
    ):
        captured["thresh"] = classification_threshold

    monkeypatch.setattr(WorldBuildingArchivist, "__init__", fake_init)
    monkeypatch.setattr(WorldBuildingArchivist, "archive_text", lambda self, t: None)
    main(["archive", "text"])
    assert captured["thresh"] == 0.8


def test_threshold_from_config(tmp_path, monkeypatch):
    cfg = tmp_path / "th.yaml"
    cfg.write_text("wba:\n  classification_threshold: 0.9\n")
    captured = {}

    def fake_init(
        self,
        store=None,
        candidate_limit=3,
        classification_threshold=0.8,
    ):
        captured["thresh"] = classification_threshold

    monkeypatch.setattr(WorldBuildingArchivist, "__init__", fake_init)
    monkeypatch.setattr(WorldBuildingArchivist, "archive_text", lambda self, t: None)
    main(["--config", str(cfg), "archive", "text"])
    assert captured["thresh"] == 0.9


def test_structure_template_from_config(tmp_path, monkeypatch):
    cfg = tmp_path / "t.yaml"
    cfg.write_text("story_structure:\n  template: [start, mid, end]\n")
    captured = {}

    def fake_init(
        self,
        *,
        candidate_limit=3,
        classification_threshold=0.8,
        structure_template=None,
    ):
        captured["template"] = structure_template

    monkeypatch.setattr(Orchestrator, "__init__", fake_init)
    monkeypatch.setattr(Orchestrator, "run", lambda self, p: None)
    main(["--config", str(cfg), "write", "x"])
    assert captured["template"] == ["start", "mid", "end"]


def _run_menu(monkeypatch, inputs):
    it = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(it))
    main(["wba-menu"])


def test_menu_load_dispatch(monkeypatch):
    called = {}

    def fake_load(self, path):
        called["path"] = path

    monkeypatch.setattr(
        WorldBuildingArchivist, "load_markdown_directory", fake_load
    )
    _run_menu(monkeypatch, ["1", "0"])
    sample_dir = os.environ.get(
        "WBA_DOCS",
        str(
            Path(__file__).resolve().parent.parent
            / "docs"
            / "wba_samples"
        ),
    )
    assert called["path"] == sample_dir


def test_menu_keyword_search(monkeypatch):
    called = {}

    def fake_search(self, term):
        called["term"] = term
        return []

    monkeypatch.setattr(WorldBuildingArchivist, "search_keyword", fake_search)
    _run_menu(monkeypatch, ["2", "hello", "0"])
    assert called["term"] == "hello"


def test_menu_semantic_search(monkeypatch):
    called = {}

    def fake_search(self, text):
        called["text"] = text
        return ({"text": "res"}, 1.0)

    monkeypatch.setattr(WorldBuildingArchivist, "search_semantic", fake_search)
    _run_menu(monkeypatch, ["3", "hi", "0"])
    assert called["text"] == "hi"


def test_menu_stats(monkeypatch):
    called = {}

    def fake_stats(self):
        called["stats"] = True
        return {}

    def fake_candidates(self):
        called["cands"] = True
        return {}

    monkeypatch.setattr(WorldBuildingArchivist, "get_type_statistics", fake_stats)
    monkeypatch.setattr(WorldBuildingArchivist, "get_candidate_counts", fake_candidates)
    _run_menu(monkeypatch, ["4", "0"])
    assert called == {"stats": True, "cands": True}


def test_menu_clear_store(monkeypatch):
    called = {}

    def fake_clear(self):
        called["cleared"] = True

    monkeypatch.setattr(WorldBuildingArchivist, "clear_rag_store", fake_clear)
    _run_menu(monkeypatch, ["5", "0"])
    assert called == {"cleared": True}
