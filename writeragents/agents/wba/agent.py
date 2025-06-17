from pathlib import Path
import logging
from collections import Counter
import re
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

    _STOPWORDS = {
        "и",
        "в",
        "во",
        "не",
        "что",
        "он",
        "на",
        "я",
        "с",
        "со",
        "как",
        "а",
        "то",
        "все",
        "она",
        "так",
        "его",
        "но",
        "да",
        "ты",
        "к",
        "у",
        "же",
        "вы",
        "за",
        "бы",
        "по",
        "только",
        "ее",
        "мне",
        "было",
        "вот",
        "от",
        "меня",
        "еще",
        "нет",
        "о",
        "из",
        "ему",
        "теперь",
        "когда",
        "даже",
        "ну",
        "вдруг",
        "ли",
        "если",
        "уже",
        "или",
        "ни",
        "быть",
        "был",
        "него",
        "до",
        "вас",
        "нибудь",
        "опять",
        "уж",
        "вам",
        "ведь",
        "там",
        "потом",
        "себя",
        "ничего",
        "ей",
        "может",
        "они",
        "тут",
        "где",
        "есть",
        "надо",
        "ней",
        "для",
        "мы",
        "тебя",
        "их",
        "чем",
        "была",
        "сам",
        "чтоб",
        "без",
        "будто",
        "чего",
        "раз",
        "тоже",
        "себе",
        "под",
        "будет",
        "ж",
        "тогда",
        "кто",
        "этот",
        "того",
        "потому",
        "этого",
        "какой",
        "совсем",
        "ним",
        "здесь",
        "этом",
        "один",
        "почти",
        "мой",
        "тем",
        "чтобы",
        "нее",
        "сейчас",
        "были",
        "куда",
        "зачем",
        "всех",
        "никогда",
        "можно",
        "при",
        "наконец",
        "два",
        "об",
        "другой",
        "хоть",
        "после",
        "над",
        "больше",
        "тот",
        "через",
        "эти",
        "нас",
        "про",
        "них",
        "какая",
        "много",
        "разве",
        "три",
        "эту",
        "моя",
        "впрочем",
        "хорошо",
        "свою",
        "этой",
        "перед",
        "иногда",
        "лучше",
        "чуть",
        "том",
        "нельзя",
        "такой",
        "им",
        "более",
        "всегда",
        "конечно",
        "всю",
        "между",
    }


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
    def load_markdown_directory(self, path: str, *, log: list[str] | None = None) -> None:
        """Load and archive all ``*.md`` files under ``path``."""
        logger = logging.getLogger(__name__)
        for md in Path(path).glob("*.md"):
            msg = f"Loading {md.name}"
            logger.info(msg)
            if log is not None:
                log.append(msg)
            text = md.read_text(encoding="utf-8")
            for block in text.split("\n\n"):
                part = block.strip()
                if not part:
                    continue
                self.archive_text(part)

    # ------------------------------------------------------------------
    def search_keyword(self, term: str) -> list[dict]:
        """Return records whose text contains ``term``."""
        term_l = term.lower()
        return [r for r in self.store.data if term_l in r["text"].lower()]

    def search_semantic(self, text: str) -> tuple[dict | None, float]:
        """Return the most semantically similar record to ``text``."""
        return self.store.find_similar(text)

    # ------------------------------------------------------------------
    def clear_rag_store(self, *, log: list[str] | None = None) -> None:
        """Remove all archived records and reset classification state."""
        logger = logging.getLogger(__name__)
        msg = "Clearing RAG store"
        logger.info(msg)
        if log is not None:
            log.append(msg)
        self.store.clear()
        self.facets = FacetManager(store=self.store)
        msg = "RAG store cleared"
        logger.info(msg)
        if log is not None:
            log.append(msg)

    def run(self, context: str) -> str:
        """Archive ``context``."""
        for block in context.split("\n\n"):
            part = block.strip()
            if not part:
                continue
            self.archive_text(part)
        return "Archived"
