from pathlib import Path
from writeragents.storage import RAGEmbeddingStore, FileRAGStore
from .faceted import FacetManager


class WorldBuildingArchivist:
    """Collects and maintains details about the fictional world."""

    def __init__(
        self,
        store: RAGEmbeddingStore | None = None,
        *,
        candidate_limit: int = 3,
        classification_threshold: float = 0.8,
    ) -> None:
        self.store = store or FileRAGStore()
        self.facets = FacetManager(
            store=self.store,
            threshold=classification_threshold,
            candidate_limit=candidate_limit,
        )
        self.candidate_limit = candidate_limit
        self.classification_threshold = classification_threshold

    def archive_text(self, text: str, **facets):
        """Store ``text`` in the RAG embedding store with optional facets."""
        metadata = {}
        for name, value in facets.items():
            rec = self.facets.classify(name, value)
            if rec:
                metadata[name] = rec["text"]
        self.store.add_entry(text, metadata=metadata)
        if isinstance(self.store, FileRAGStore):
            self.store.save()

    # ------------------------------------------------------------------
    def load_markdown_directory(self, path: str) -> None:
        """Load and archive all ``*.md`` files under ``path``."""
        for md in Path(path).glob("*.md"):
            text = md.read_text(encoding="utf-8")
            facets: dict[str, str] = {}
            for line in text.splitlines()[:5]:
                lower = line.lower()
                if lower.startswith("type:"):
                    facets["type"] = line.split(":", 1)[1].strip()
                elif lower.startswith("era:"):
                    facets["era"] = line.split(":", 1)[1].strip()
            self.archive_text(text, **facets)

    # ------------------------------------------------------------------
    def search_keyword(self, term: str) -> list[dict]:
        """Return records whose text contains ``term``."""
        term_l = term.lower()
        return [r for r in self.store.data if term_l in r["text"].lower()]

    def search_semantic(self, text: str) -> tuple[dict | None, float]:
        """Return the most semantically similar record to ``text``."""
        return self.store.find_similar(text)

    # ------------------------------------------------------------------
    def get_type_statistics(self) -> dict[str, int]:
        """Return counts of archived records for each content type."""
        mgr = self.facets._get_manager("type")
        return mgr.get_type_counts()

    def get_candidate_counts(self) -> dict[str, int]:
        """Return current unresolved type candidate counts."""
        mgr = self.facets._get_manager("type")
        return mgr.get_candidate_counts()

    # ------------------------------------------------------------------
    def clear_rag_store(self) -> None:
        """Remove all archived records and reset classification state."""
        self.store.clear()
        self.facets = FacetManager(store=self.store)

    def run(self, context: str) -> str:
        """Archive ``context`` while extracting basic facet information."""

        facets: dict[str, str] = {}
        for line in context.splitlines()[:5]:
            lower = line.lower()
            if lower.startswith("type:"):
                facets["type"] = line.split(":", 1)[1].strip()
            elif lower.startswith("era:"):
                facets["era"] = line.split(":", 1)[1].strip()

        self.archive_text(context, **facets)
        return "Archived"
