from __future__ import annotations

from typing import Optional

from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.llm import LLMClient


class RAGSearchAgent:
    """Retrieval augmented generation agent for fact gathering."""

    def __init__(
        self,
        archivist: Optional[WorldBuildingArchivist] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.archivist = archivist or WorldBuildingArchivist()
        self.llm = llm_client or LLMClient()

    # ------------------------------------------------------------------
    def run(self, query: str, *, log: list[str] | None = None) -> str:
        """Return an answer to ``query`` based on archived context.

        LLM interaction details are stored in ``log`` if provided.
        """
        record, _score = self.archivist.search_semantic(query)
        if not record:
            return ""
        prompt = (
            "Use the following context to answer the query:\n"
            f"{record['text']}\nQuery: {query}"
        )
        return self.llm.generate(prompt, log=log)
