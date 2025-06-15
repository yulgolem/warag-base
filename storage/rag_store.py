class RAGEmbeddingStore:
    """Simple in-memory store for text embeddings."""

    def __init__(self):
        self.data = []
        self._next_id = 1

    def _embed(self, text):
        import hashlib

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # return first 8 bytes as ints for deterministic small embedding
        return [b for b in digest[:8]]

    def add_entry(self, text):
        embedding = self._embed(text)
        record = {
            "id": self._next_id,
            "text": text,
            "embedding": embedding,
        }
        self.data.append(record)
        self._next_id += 1
        return record
