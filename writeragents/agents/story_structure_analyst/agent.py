from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence


class StoryStructureAnalyst:
    """Analyze structural aspects of a text."""

    def __init__(self, template: Optional[Sequence[str]] = None) -> None:
        """Create analyst with optional story ``template``.

        Parameters
        ----------
        template:
            Ordered list of section names defining the narrative structure.
            Text is divided evenly among these sections. Defaults to a
            three-act scheme.
        """
        self.template = list(template) if template else [
            "act_i",
            "act_ii",
            "act_iii",
        ]

    # ------------------------------------------------------------------
    def analyze_pacing(self, text: str) -> str:
        """Return ``fast``, ``moderate`` or ``slow`` based on sentence length."""
        sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
        if not sentences:
            return "unknown"
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words < 10:
            return "fast"
        if avg_words > 20:
            return "slow"
        return "moderate"

    # ------------------------------------------------------------------
    def analyze_structure(self, text: str) -> Dict[str, str]:
        """Return segments of ``text`` according to ``self.template``."""
        words = text.split()
        if not words:
            return {name: "" for name in self.template}

        seg_size = max(1, len(words) // len(self.template))
        acts: Dict[str, str] = {}
        for i, name in enumerate(self.template):
            start = i * seg_size
            end = len(words) if i == len(self.template) - 1 else (i + 1) * seg_size
            acts[name] = " ".join(words[start:end])
        return acts

    # ------------------------------------------------------------------
    def find_unresolved_subplots(self, text: str) -> List[str]:
        """Return sentences mentioning subplots without a resolution."""
        unresolved: List[str] = []
        for sent in re.split(r"[.!?]", text):
            lower = sent.lower()
            if "subplot" in lower and not re.search(r"resolved|concluded", lower):
                m = re.search(r"subplot\s+(\w+)", sent, re.IGNORECASE)
                unresolved.append(m.group(1) if m else sent.strip())
        return unresolved

    # ------------------------------------------------------------------
    def run(self, text: str) -> str:
        """Return a human readable structure report for ``text``."""
        pacing = self.analyze_pacing(text)
        acts = self.analyze_structure(text)
        subplots = self.find_unresolved_subplots(text)

        report_lines = [
            f"Pacing: {pacing}",
            "Structure breakdown:",
        ]
        for name in self.template:
            report_lines.append(f"  {name} words: {len(acts[name].split())}")
        if subplots:
            report_lines.append("Unresolved subplots: " + ", ".join(subplots))
        else:
            report_lines.append("No unresolved subplots detected")
        return "\n".join(report_lines)
