import json
import importlib
import threading

import src.utils.logging_utils as logging_utils


def setup_manager(tmp_path, monkeypatch):
    logging_utils.LoggerManager.reset()
    importlib.reload(logging_utils)
    monkeypatch.setattr(logging_utils, "LOG_FILE_PATH", tmp_path / "app.jsonl")
    logging_utils.LoggerManager.reset()
    return logging_utils.LoggerManager()


def test_json_formatting(tmp_path, monkeypatch):
    manager = setup_manager(tmp_path, monkeypatch)
    logger = manager.get_logger("agents")
    logger.info("hello")
    log_file = tmp_path / "app.jsonl"
    data = json.loads(log_file.read_text(encoding="utf-8"))
    assert data["message"] == "hello"
    assert data["logger"] == "agents"


def test_thread_safety(tmp_path, monkeypatch):
    manager = setup_manager(tmp_path, monkeypatch)

    def worker(i: int) -> None:
        manager.log_with_extra("agents", "info", f"msg{i}", thread=i)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log_file = tmp_path / "app.jsonl"
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5
    indices = {json.loads(line)["thread"] for line in lines}
    assert indices == set(range(5))


def test_log_file_creation(tmp_path, monkeypatch):
    manager = setup_manager(tmp_path, monkeypatch)
    manager.log_with_extra("ui", "info", "created")
    assert (tmp_path / "app.jsonl").exists()


def test_extra_data_structured(tmp_path, monkeypatch):
    manager = setup_manager(tmp_path, monkeypatch)
    manager.log_with_extra("database", "warning", "warn", foo="bar", count=1)
    data = json.loads((tmp_path / "app.jsonl").read_text(encoding="utf-8"))
    assert data["foo"] == "bar"
    assert data["count"] == 1
    assert data["level"] == "WARNING"

