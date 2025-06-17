from writeragents.storage.file_store import FileRAGStore


def test_file_ragstore_persistence(tmp_path):
    path = tmp_path / "store.json"
    store1 = FileRAGStore(path=str(path))
    store1.add_entry("hello", metadata={"type": "note"})
    store1.save()

    assert path.exists()

    store2 = FileRAGStore(path=str(path))
    assert store2.data[0]["text"] == "hello"
    assert store2.data[0]["metadata"]["type"] == "note"
    assert store2._next_id == 2


def test_file_ragstore_clear(tmp_path):
    path = tmp_path / "store.json"
    store = FileRAGStore(path=str(path))
    store.add_entry("bye")
    store.save()
    assert path.exists()
    store.clear()
    assert not path.exists()
    assert store.data == []
