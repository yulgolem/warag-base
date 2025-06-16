from __future__ import annotations

import re
from typing import Dict, List


class StoryStructureAnalyst:
    """Analyze structural aspects of a text."""

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
    def analyze_three_act_structure(self, text: str) -> Dict[str, str]:
        """Split ``text`` into approximate three acts and return them."""
        words = text.split()
        if not words:
            return {"act_i": "", "act_ii": "", "act_iii": ""}
        third = max(1, len(words) // 3)
        return {
            "act_i": " ".join(words[:third]),
            "act_ii": " ".join(words[third:2 * third]),
            "act_iii": " ".join(words[2 * third :]),
        }

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
        acts = self.analyze_three_act_structure(text)
        subplots = self.find_unresolved_subplots(text)

        report_lines = [
            f"Pacing: {pacing}",
            "Three-act breakdown:",
            f"  Act I words: {len(acts['act_i'].split())}",
            f"  Act II words: {len(acts['act_ii'].split())}",
            f"  Act III words: {len(acts['act_iii'].split())}",
        ]
        if subplots:
            report_lines.append("Unresolved subplots: " + ", ".join(subplots))
        else:
            report_lines.append("No unresolved subplots detected")
        return "\n".join(report_lines)
