from __future__ import annotations

import re
from typing import List

from writeragents.agents.wba.agent import WorldBuildingArchivist


class ConsistencyChecker:
    """Ensures story events remain coherent and track facts."""

    def __init__(self, archivist: WorldBuildingArchivist | None = None) -> None:
        # Allow dependency injection of the archivist for testing
        self.archivist = archivist or WorldBuildingArchivist()

    # ------------------------------------------------------------------
    def _parse_births(self, text: str) -> list[tuple[str, int]]:
        pattern = re.compile(r"(\b[A-Z][a-zA-Z]+) was born in (\d{3,4})")
        return [(m.group(1), int(m.group(2))) for m in pattern.finditer(text)]

    def _parse_is(self, text: str, negate: bool = False) -> list[tuple[str, str]]:
        if negate:
            pat = re.compile(r"(\b[A-Z][a-zA-Z]+) is not ([^.]+)")
        else:
            pat = re.compile(r"(\b[A-Z][a-zA-Z]+) is ([^.]+)")
        return [(m.group(1), m.group(2).strip()) for m in pat.finditer(text)]

    # ------------------------------------------------------------------
    def check(self, text: str) -> list[str]:
        """Return a list of detected issues for ``text``."""
        issues: list[str] = []
        archive = [rec.get("text", "") for rec in self.archivist.store.data]

        births = self._parse_births(text)
        for name, year in births:
            for rec in archive:
                for n2, y2 in self._parse_births(rec):
                    if n2 == name and y2 != year:
                        issues.append(
                            f"Timeline mismatch for {name}: {year} vs {y2}" 
                        )
                        break

        pos = self._parse_is(text)
        neg = self._parse_is(text, negate=True)
        for name, desc in pos:
            for rec in archive:
                if (name, desc) in self._parse_is(rec, negate=True):
                    issues.append(
                        f"Contradiction: {name} is {desc} but archive says not"
                    )
                    break
        for name, desc in neg:
            for rec in archive:
                if (name, desc) in self._parse_is(rec, negate=False):
                    issues.append(
                        f"Contradiction: archive says {name} is {desc}"
                    )
                    break

        return issues

    # ------------------------------------------------------------------
    def run(self, context: str) -> str:
        issues = self.check(context)
        return "\n".join(issues)


_default_checker: ConsistencyChecker | None = None


def check_consistency(text: str) -> List[str]:
    """Convenience API that checks ``text`` using a default checker."""
    global _default_checker
    if _default_checker is None:
        _default_checker = ConsistencyChecker()
    return _default_checker.check(text)
