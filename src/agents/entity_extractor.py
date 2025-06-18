from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import requests
from crewai import Agent, Task

from src.models.entities import Entity
from src.utils.logging_utils import get_agent_logger, log_entity_extraction

DEFAULT_ENTITY_TYPES = ["person", "location", "organization", "concept", "object"]

EXTRACTION_PROMPT_TEMPLATE = """### Task: Extract named entities from the text chunk below.

### Entity Types to Extract:
{entity_types}

### Text Chunk:
{text}

### Rules:
1. Extract only entities that clearly belong to specified types
2. Assign confidence score 0.7-1.0 based on context clarity
3. Include all text variations in mentions array
4. Keep descriptions under 100 characters
5. Focus on narrative-relevant entities only
6. Provide context (50-100 chars around mention)

### Output Format (valid JSON only, no explanations):
{{
  "entities": [
    {{
      "name": "entity_name",
      "type": "entity_type", 
      "description": "brief_description",
      "mentions": ["mention1", "mention2"],
      "confidence": 0.95,
      "context": "text_fragment_with_mention"
    }}
  ]
}}

### Response:"""


class EntityExtractorAgent:
    """CrewAI agent for extracting entities using NuExtract via Ollama."""

    def __init__(self, ollama_base_url: str = "http://ollama:11434") -> None:
        self.ollama_url = ollama_base_url.rstrip("/")
        self.model_name = "nuextract"
        self.logger = get_agent_logger()
        self.max_retries = 3
        self.base_delay = 1.0

    def create_agent(self) -> Agent:
        return Agent(
            role="Named Entity Recognition Specialist",
            goal="Extract entities from text chunks with high accuracy",
            backstory=(
                "Expert in identifying persons, locations, organizations, concepts, and objects in narrative texts."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[],
            max_iter=1,
            memory=False,
        )

    def create_extraction_task(self, chunk_data: Dict[str, Any], entity_types: List[str]) -> Task:
        return Task(
            description=f"Extract entities of types {entity_types} from text chunk {chunk_data['chunk_id']}",
            agent=self.create_agent(),
            expected_output="List of Entity objects in JSON format with high confidence scores",
        )

    # ------------------------------------------------------------------
    # Core extraction logic
    # ------------------------------------------------------------------
    def extract_entities(
        self,
        chunk_text: str,
        chunk_metadata: Dict[str, Any],
        entity_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
    ) -> List[Entity]:
        if not chunk_text or not chunk_text.strip():
            return []

        if entity_types is None:
            entity_types = DEFAULT_ENTITY_TYPES.copy()

        prompt = self._build_extraction_prompt(chunk_text, entity_types)
        start_time = time.time()
        try:
            response = self._retry_with_backoff(self._call_ollama_api, prompt)
        except Exception as e:  # pragma: no cover - network issues
            self.logger.error(
                f"Failed to extract entities from chunk {chunk_metadata.get('chunk_id')}: {e}"
            )
            return []

        if not self._validate_ollama_response(response):
            self.logger.error(
                f"Failed to extract entities from chunk {chunk_metadata.get('chunk_id')}: invalid response"
            )
            return []

        entities = self._parse_entities_response(
            response.get("response", ""), chunk_metadata, confidence_threshold
        )
        elapsed = time.time() - start_time
        self.logger.info(
            f"Processing chunk {chunk_metadata.get('chunk_id')}: {len(entities)} entities extracted"
        )
        log_entity_extraction(chunk_metadata.get("chunk_id", ""), len(entities), elapsed, self.model_name)
        return entities

    def extract_entities_batch(
        self,
        chunks: List[Dict[str, Any]],
        entity_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
    ) -> List[List[Entity]]:
        results: List[List[Entity]] = []
        for chunk in chunks:
            try:
                ents = self.extract_entities(
                    chunk.get("text", ""),
                    chunk,
                    entity_types,
                    confidence_threshold,
                )
            except Exception as e:  # pragma: no cover - unexpected errors
                self.logger.error(
                    f"Failed to extract entities from chunk {chunk.get('chunk_id')}: {e}"
                )
                ents = []
            results.append(ents)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _retry_with_backoff(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Final attempt failed: {e}")
                    raise
                delay = self.base_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s")
                time.sleep(delay)

    def _call_ollama_api(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _validate_ollama_response(self, response_data: Dict[str, Any]) -> bool:
        if not isinstance(response_data, dict):
            return False
        if "response" not in response_data:
            return False
        return True

    def _build_extraction_prompt(self, text: str, entity_types: List[str]) -> str:
        return EXTRACTION_PROMPT_TEMPLATE.format(
            entity_types=", ".join(entity_types),
            text=text,
        )

    def _parse_entities_response(
        self,
        response_text: str,
        chunk_metadata: Dict[str, Any],
        confidence_threshold: float,
    ) -> List[Entity]:
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Failed to parse JSON for chunk {chunk_metadata.get('chunk_id')}: {e}"
            )
            return []
        if not isinstance(data, dict) or "entities" not in data:
            self.logger.error(
                f"Failed to parse JSON for chunk {chunk_metadata.get('chunk_id')}: missing entities"
            )
            return []

        entities: List[Entity] = []
        for item in data.get("entities", []):
            try:
                confidence = float(item.get("confidence", 0))
            except (TypeError, ValueError):
                confidence = 0.0
            if confidence < confidence_threshold:
                self.logger.warning(
                    f"Low confidence entity filtered: {item.get('name')} ({confidence})"
                )
                continue
            try:
                entity = Entity(
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    description=item.get("description"),
                    mentions=item.get("mentions", []) or [],
                    confidence=confidence,
                    source_file=chunk_metadata.get("file_name", ""),
                    chunk_id=chunk_metadata.get("chunk_id", ""),
                    source_chunk=chunk_metadata.get("text", ""),
                    context=item.get("context", ""),
                )
                entities.append(entity)
            except Exception as e:  # pragma: no cover - validation issues
                self.logger.error(f"Invalid entity data: {e}")
        return entities
