import pytest

from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.storage import RAGEmbeddingStore


def test_archive_text_stores_record():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text("hello world")
    assert len(store.data) == 1
    record = store.data[0]
    assert record["text"] == "hello world"
    assert isinstance(record["embedding"], list)
    assert len(record["embedding"]) == 8


def test_clear_rag_store_resets_data():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text("text")
    assert store.data
    wba.clear_rag_store()
    assert store.data == []

