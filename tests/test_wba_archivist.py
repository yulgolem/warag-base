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


def test_run_archives_with_facets():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store, candidate_limit=1)
    msg = wba.run("Type: Location\nEra: Bronze\nCity of gold")
    assert msg == "Archived"
    rec = store.data[-1]
    assert rec["metadata"]["type"] == "Location"
    assert rec["metadata"]["era"] == "Bronze"

