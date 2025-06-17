"""Writer agent that delegates text generation to an LLM service."""

from __future__ import annotations

from typing import Optional

from writeragents.llm import LLMClient


class WriterAgent:
    """Coordinates other agents and produces the final narrative."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm = llm_client or LLMClient()

    # ------------------------------------------------------------------
    def run(self, prompt: str) -> str:
        """Generate a text response for ``prompt`` using the LLM."""
        return self.llm.generate(prompt)
