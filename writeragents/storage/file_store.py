import json
import os
from .rag_store import RAGEmbeddingStore

class FileRAGStore(RAGEmbeddingStore):
    """RAGEmbeddingStore with simple JSON persistence."""

    def __init__(self, path: str = "rag_store.json") -> None:
        super().__init__()
        self.path = path
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.data = data.get("data", [])
            self._next_id = data.get("_next_id", 1)
        else:
            self.data = []
            self._next_id = 1

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump({"data": self.data, "_next_id": self._next_id}, fh)
