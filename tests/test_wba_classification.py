from writeragents.agents.wba.classification import ContentTypeManager
from writeragents.storage import RAGEmbeddingStore


def test_add_and_search_and_autocreate():
    store = RAGEmbeddingStore()
    manager = ContentTypeManager(store=store, threshold=0.9)

    # Add a type and ensure it is stored
    t1 = manager.add_type("Character")
    assert t1["text"] == "Character"
    assert t1["metadata"]["category"] == manager.CATEGORY

    # Classify similar name should reuse existing type
    found = manager.classify("character")
    assert found["id"] == t1["id"]
    assert len([r for r in store.data if r.get("metadata", {}).get("category") == manager.CATEGORY]) == 1

    # Classify new unrelated type should create a new entry
    t2 = manager.classify("Location")
    assert t2["text"] == "Location"
    assert len([r for r in store.data if r.get("metadata", {}).get("category") == manager.CATEGORY]) == 2

