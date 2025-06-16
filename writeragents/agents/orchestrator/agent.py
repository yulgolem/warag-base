from __future__ import annotations

from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.agents.consistency_checker.agent import ConsistencyChecker
from writeragents.agents.creativity_assistant.agent import CreativityAssistant
from writeragents.agents.rag_search.agent import RAGSearchAgent
from writeragents.agents.writer_agent.agent import WriterAgent


class Orchestrator:
    """Route user requests to the appropriate specialized agent."""

    def __init__(self) -> None:
        self.wba = WorldBuildingArchivist()
        self.consistency_checker = ConsistencyChecker()
        self.creativity_assistant = CreativityAssistant()
        self.rag_search_agent = RAGSearchAgent()
        self.writer_agent = WriterAgent()

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

        return self.writer_agent.run(request)

