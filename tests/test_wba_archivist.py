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


def test_run_assigns_semantic_type():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store, candidate_limit=1)
    msg = wba.run("Рыцари охраняют замок")
    assert msg == "Archived"
    rec = store.data[-1]
    assert rec["metadata"]["type"] == "Рыцари"




def test_load_markdown_directory_multi_paragraph(tmp_path):
    md = tmp_path / "multi.md"
    md.write_text(
        "Рыцари защищают замок.\n\nТорговля процветает.",
        encoding="utf-8",
    )
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store, candidate_limit=1)
    wba.load_markdown_directory(str(tmp_path))
    types = [r["metadata"]["type"] for r in store.data if "type" in r.get("metadata", {})]
    assert "Рыцари" in types
    assert "Торговля" in types

