from __future__ import annotations

import math
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

from writeragents.storage import RAGEmbeddingStore


class ContentTypeManager:
    """Manage content-type metadata using a ``RAGEmbeddingStore``.

    Parameters
    ----------
    store:
        Optional :class:`~writeragents.storage.rag_store.RAGEmbeddingStore` in
        which types are stored. If not provided, a new in-memory store is used.
    threshold:
        Similarity threshold for reusing an existing type.
    candidate_limit:
        How many times an unknown name must be seen before a new type is
        automatically created.
    """

    CATEGORY = "content-type"

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
        self._candidate_counts: dict[str, int] = {}
        self._classification_log: list[str] = []

    # Helper methods -----------------------------------------------------
    def _embed(self, text: str) -> list[int]:
        return self.store._embed(text)

    @staticmethod
    def _similarity(a: list[int], b: list[int]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # Public API ---------------------------------------------------------
    def add_type(self, name: str) -> dict:
        """Add a new content type to the store."""
        record = self.store.add_entry(name, metadata={"category": self.CATEGORY})
        msg = f"Created new type '{name}'"
        logger.info(msg)
        self._classification_log.append(msg)
        return record

    def find_closest_type(self, name: str) -> Tuple[dict | None, float]:
        """Return the closest stored type to ``name`` and similarity score."""
        emb = self._embed(name)
        best = None
        best_score = 0.0
        for rec in self.store.data:
            if rec.get("metadata", {}).get("category") != self.CATEGORY:
                continue
            score = self._similarity(emb, rec["embedding"])
            if score > best_score:
                best = rec
                best_score = score
        return best, best_score

    def classify(self, name: str) -> dict | None:
        """Return an existing type matching ``name`` or create a new one.

        The name is normalized and tracked internally. If a matching stored
        type meets the similarity ``threshold`` the existing record is
        returned. Otherwise the name must be seen ``candidate_limit`` times
        before a new type is added.
        """
        rec, score = self.find_closest_type(name)
        norm = name.lower()

        if rec and score >= self.threshold:
            # reset tracking for known names
            self._candidate_counts.pop(norm, None)
            msg = (
                f"Reusing type '{rec['text']}' for '{name}' with score {score:.2f}"
            )
            logger.info(msg)
            self._classification_log.append(msg)
            return rec

        count = self._candidate_counts.get(norm, 0) + 1
        if count >= self.candidate_limit:
            self._candidate_counts.pop(norm, None)
            return self.add_type(name)

        self._candidate_counts[norm] = count
        msg = f"Incremented candidate count for '{norm}' to {count}"
        logger.info(msg)
        self._classification_log.append(msg)
        return None

    # ------------------------------------------------------------------
    def get_type_counts(self) -> dict[str, int]:
        """Return a mapping of stored type names to usage count."""
        counts: dict[str, int] = {}
        for rec in self.store.data:
            meta = rec.get("metadata", {})
            if meta.get("category") == self.CATEGORY:
                # skip records that represent the types themselves
                continue
            type_name = meta.get("type")
            if type_name:
                counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def get_candidate_counts(self) -> dict[str, int]:
        """Return how many times unknown type names have been seen."""
        return dict(self._candidate_counts)

    def get_classification_log(self) -> list[str]:
        """Return recorded classification events for auditing."""
        return list(self._classification_log)

