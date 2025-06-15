import math


class RAGEmbeddingStore:
    """Simple in-memory store for text embeddings."""

    def __init__(self):
        self.data = []
        self._next_id = 1

    def _embed(self, text: str) -> list[int]:
        """Return a simple deterministic embedding for ``text``."""
        counts = [0] * 8
        for ch in text.lower():
            idx = ord(ch) - 97
            if 0 <= idx < 8:
                counts[idx] += 1
        return counts

    def add_entry(self, text: str, metadata: dict | None = None) -> dict:
        """Store ``text`` and optional ``metadata`` in the embedding store."""
        embedding = self._embed(text)
        record = {
            "id": self._next_id,
            "text": text,
            "embedding": embedding,
        }
        if metadata is not None:
            record["metadata"] = metadata
        self.data.append(record)
        self._next_id += 1
        return record

    @staticmethod
    def _similarity(a: list[int], b: list[int]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def find_similar(self, text: str) -> tuple[dict | None, float]:
        """Return the most similar record to ``text`` and the similarity score."""
        embedding = self._embed(text)
        best = None
        best_score = 0.0
        for record in self.data:
            score = self._similarity(embedding, record["embedding"])
            if score > best_score:
                best = record
                best_score = score
        return best, best_score

