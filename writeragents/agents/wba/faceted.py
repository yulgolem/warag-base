from __future__ import annotations

from writeragents.storage import RAGEmbeddingStore
from .classification import ContentTypeManager


class FacetManager:
    """Manage classification of arbitrary facets using ``ContentTypeManager``.

    Each facet name (like ``"type"`` or ``"era"``) gets its own
    :class:`ContentTypeManager`. Facet values are stored as meta-documents with
    ``{"category": f"facet-{facet}"}`` so they can be queried separately.
    """

    def __init__(
        self,
        store: RAGEmbeddingStore | None = None,
        threshold: float = 0.8,
        *,
        candidate_limit: int = 3,
    ) -> None:
        self.store = store or RAGEmbeddingStore()
        self.threshold = threshold
        self.candidate_limit = candidate_limit
        self._managers: dict[str, ContentTypeManager] = {}

    # ------------------------------------------------------------------
    def _get_manager(self, facet: str) -> ContentTypeManager:
        mgr = self._managers.get(facet)
        if mgr is None:
            mgr = ContentTypeManager(
                store=self.store,
                threshold=self.threshold,
                candidate_limit=self.candidate_limit,
            )
            # Mark records created by this manager with the facet category
            mgr.CATEGORY = f"facet-{facet}"
            self._managers[facet] = mgr
        return mgr

    def classify(self, facet: str, value: str) -> dict | None:
        """Classify ``value`` for ``facet`` and return the stored record if known."""
        return self._get_manager(facet).classify(value)

    def get_candidate_counts(self, facet: str) -> dict[str, int]:
        """Return unresolved candidate counts for ``facet``."""
        mgr = self._managers.get(facet)
        return mgr.get_candidate_counts() if mgr else {}
