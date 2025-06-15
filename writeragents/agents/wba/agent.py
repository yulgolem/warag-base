from pathlib import Path
from writeragents.storage import RAGEmbeddingStore, FileRAGStore
from .classification import ContentTypeManager


class WorldBuildingArchivist:
    """Collects and maintains details about the fictional world."""

    def __init__(self, store: RAGEmbeddingStore | None = None):
        self.store = store or FileRAGStore()
        self.types = ContentTypeManager(store=self.store)

    def archive_text(self, text: str, type_name: str | None = None, **metadata):
        """Store ``text`` in the RAG embedding store with optional metadata."""
        if type_name:
            rec = self.types.classify(type_name)
            if rec:
                metadata["type"] = rec["text"]
        self.store.add_entry(text, metadata=metadata)
        if isinstance(self.store, FileRAGStore):
            self.store.save()

    # ------------------------------------------------------------------
    def load_markdown_directory(self, path: str) -> None:
        """Load and archive all ``*.md`` files under ``path``."""
        for md in Path(path).glob("*.md"):
            text = md.read_text(encoding="utf-8")
            type_name = None
            for line in text.splitlines():
                if line.lower().startswith("type:"):
                    type_name = line.split(":", 1)[1].strip()
                    break
            self.archive_text(text, type_name=type_name, filename=md.name)

    # ------------------------------------------------------------------
    def search_keyword(self, term: str) -> list[dict]:
        """Return records whose text contains ``term``."""
        term_l = term.lower()
        return [r for r in self.store.data if term_l in r["text"].lower()]

    def search_semantic(self, text: str) -> tuple[dict | None, float]:
        """Return the most semantically similar record to ``text``."""
        return self.store.find_similar(text)

    # ------------------------------------------------------------------
    def clear_archive(self) -> None:
        """Remove all archived records and reset classification state."""
        self.store.clear()
        self.types = ContentTypeManager(store=self.store)

    # ------------------------------------------------------------------
    def get_type_statistics(self) -> dict[str, int]:
        """Return counts of archived records for each content type."""
        return self.types.get_type_counts()

    def get_candidate_counts(self) -> dict[str, int]:
        """Return current unresolved type candidate counts."""
        return self.types.get_candidate_counts()

    def run(self, context):
        # TODO: implement world building logic
        pass
