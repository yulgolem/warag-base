import sqlite3
import redis
from writeragents.storage.short_term import RedisMemory
from writeragents.storage.long_term import DatabaseMemory


def test_redis_memory(monkeypatch):
    class FakeRedis:
        def __init__(self, host="localhost", port=6379, db=0):
            self.kw = {"host": host, "port": port, "db": db}
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value):
            self.store[key] = value

    monkeypatch.setattr(redis, "Redis", FakeRedis)
    mem = RedisMemory()
    mem.set("a", "1")
    assert mem.get("a") == "1"
    assert mem.client.kw == {"host": "localhost", "port": 6379, "db": 0}


def test_redis_memory_custom(monkeypatch):
    class FakeRedis:
        def __init__(self, host="localhost", port=6379, db=0):
            self.kw = {"host": host, "port": port, "db": db}
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value):
            self.store[key] = value

    monkeypatch.setattr(redis, "Redis", FakeRedis)
    mem = RedisMemory(host="h", port=6380, db=2)
    assert mem.client.kw == {"host": "h", "port": 6380, "db": 2}


def test_database_memory(tmp_path):
    db_path = tmp_path / "mem.db"
    with DatabaseMemory(url=f"sqlite:///{db_path}") as mem:
        mem.store("hello")
        rows = mem.fetch("SELECT data FROM memory")
        assert rows[0][0] == "hello"
