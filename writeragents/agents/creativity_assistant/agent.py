from __future__ import annotations

from typing import Optional

from writeragents.llm import LLMClient


class CreativityAssistant:
    """Helps generate new ideas and stylistic enhancements."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm = llm_client or LLMClient()

    # ------------------------------------------------------------------
    def run(self, context: str) -> str:
        """Return creative suggestions for ``context``."""
        prompt = (
            "Suggest creative improvements to the following text:\n" f"{context}"
        )
        return self.llm.generate(prompt)
