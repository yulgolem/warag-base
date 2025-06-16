from writeragents.agents.consistency_checker import agent as cc_mod
from writeragents.agents.consistency_checker.agent import ConsistencyChecker
from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.storage import RAGEmbeddingStore


def test_birth_year_conflict():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text("Alice was born in 1990.")
    checker = ConsistencyChecker(archivist=wba)
    issues = checker.check("Alice was born in 1985.")
    assert any("Timeline mismatch" in i for i in issues)


def test_negated_fact_conflict():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text("Bob is a wizard.")
    checker = ConsistencyChecker(archivist=wba)
    issues = checker.check("Bob is not a wizard.")
    assert any("Contradiction" in i for i in issues)


def test_module_function_uses_default_checker():
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text("Clara is a pilot.")
    cc_mod._default_checker = ConsistencyChecker(archivist=wba)
    issues = cc_mod.check_consistency("Clara is not a pilot.")
    assert issues
