from __future__ import annotations

from typing import Sequence

from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.agents.consistency_checker.agent import ConsistencyChecker
from writeragents.agents.creativity_assistant.agent import CreativityAssistant
from writeragents.agents.rag_search.agent import RAGSearchAgent
from writeragents.agents.writer_agent.agent import WriterAgent
from writeragents.agents.story_structure_analyst.agent import StoryStructureAnalyst


class Orchestrator:
    """Route user requests to the appropriate specialized agent."""

    def __init__(
        self,
        *,
        candidate_limit: int = 3,
        classification_threshold: float = 0.8,
        structure_template: Sequence[str] | None = None,
    ) -> None:
        self.wba = WorldBuildingArchivist(
            candidate_limit=candidate_limit,
            classification_threshold=classification_threshold,
        )
        self.consistency_checker = ConsistencyChecker()
        self.creativity_assistant = CreativityAssistant()
        self.rag_search_agent = RAGSearchAgent()
        self.writer_agent = WriterAgent()
        self.structure_analyst = StoryStructureAnalyst(template=structure_template)

    # ------------------------------------------------------------------
    def _parse_intent(self, request: str) -> tuple[str | None, str]:
        """Return (intent, content) for ``request``.

        Requests of the form ``"intent: rest"`` are parsed into an intent name
        and the remaining content.  If no intent prefix is found, ``intent`` is
        ``None`` and ``content`` is the original request.
        """
        if ":" in request:
            command, rest = request.split(":", 1)
            return command.strip().lower(), rest.strip()
        return None, request

    # ------------------------------------------------------------------
    def run(self, request: str):
        """Process ``request`` and return a response string."""
        intent, content = self._parse_intent(request)

        if intent == "archive":
            self.wba.archive_text(content)
            return "Archived"
        if intent in {"check", "consistency"}:
            result = self.consistency_checker.run(content)
            return result or "Checked"
        if intent in {"creative", "creativity", "brainstorm"}:
            result = self.creativity_assistant.run(content)
            return result or "Created"
        if intent == "search":
            result = self.rag_search_agent.run(content)
            return result if result is not None else ""
        if intent in {"structure", "analysis", "analyze"}:
            return self.structure_analyst.run(content)

        return self.writer_agent.run(request)

