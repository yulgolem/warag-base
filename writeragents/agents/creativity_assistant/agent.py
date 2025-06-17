from __future__ import annotations

from typing import Optional

from writeragents.llm import LLMClient


class CreativityAssistant:
    """Helps generate new ideas and stylistic enhancements."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm = llm_client or LLMClient()

    # ------------------------------------------------------------------
    def run(self, context: str, *, log: list[str] | None = None) -> str:
        """Return creative suggestions for ``context``.

        Interactions with the LLM are appended to ``log`` if provided.
        """
        prompt = (
            "Suggest creative improvements to the following text:\n" f"{context}"
        )
        return self.llm.generate(prompt, log=log)
