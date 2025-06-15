from __future__ import annotations

import math
from typing import Tuple

from writeragents.storage import RAGEmbeddingStore


class ContentTypeManager:
    """Manage content-type metadata using a ``RAGEmbeddingStore``."""

    CATEGORY = "content-type"

    def __init__(self, store: RAGEmbeddingStore | None = None, threshold: float = 0.8):
        self.store = store or RAGEmbeddingStore()
        self.threshold = threshold

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
        return self.store.add_entry(name, metadata={"category": self.CATEGORY})

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

    def classify(self, name: str) -> dict:
        """Return an existing type matching ``name`` or create a new one."""
        rec, score = self.find_closest_type(name)
        if rec and score >= self.threshold:
            return rec
        return self.add_type(name)

