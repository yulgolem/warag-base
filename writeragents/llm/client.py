"""Client for interacting with a language model service."""
from __future__ import annotations

import os
from importlib import resources
from typing import Any, Dict, Optional

import logging
import requests

logger = logging.getLogger(__name__)

from writeragents.cli import load_config


class LLMClient:
    """Simple HTTP client for OpenAI-compatible endpoints."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        if endpoint is None or model is None or api_key is None:
            cfg = self._load_default_config()
            endpoint = endpoint or cfg.get("endpoint")
            model = model or cfg.get("model")
            api_key = api_key or cfg.get("api_key")
        self.endpoint = str(endpoint).rstrip("/")
        self.model = model
        self.api_key = api_key

    # ------------------------------------------------------------------
    @staticmethod
    def _load_default_config() -> Dict[str, Any]:
        cfg_path = os.environ.get(
            "WRITERAG_CONFIG",
            str(resources.files("writeragents").joinpath("config/local.yaml")),
        )
        cfg = load_config(cfg_path)
        return cfg.get("llm", {})

    # ------------------------------------------------------------------
    def generate(self, prompt: str) -> str:
        """Return model output for ``prompt`` using the configured endpoint."""

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if "11434" in self.endpoint or "ollama" in self.endpoint:
            url = f"{self.endpoint}/api/generate"
            payload = {"model": self.model, "prompt": prompt, "stream": False}
        else:
            url = f"{self.endpoint}/chat/completions"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("LLM request failed: %s", exc)
            return ""
        if "choices" in data:
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
        return data.get("response", "")
