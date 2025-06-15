from writeragents.storage import RAGEmbeddingStore


class WorldBuildingArchivist:
    """Collects and maintains details about the fictional world."""

    def __init__(self, store=None):
        self.store = store or RAGEmbeddingStore()

    def archive_text(self, text):
        """Store text in the RAG embedding store."""
        self.store.add_entry(text)

    def run(self, context):
        # TODO: implement world building logic
        pass
