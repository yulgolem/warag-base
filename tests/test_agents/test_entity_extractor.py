import json
import requests

import pytest

from src.agents.entity_extractor import EntityExtractorAgent


class TestEntityExtractorAgent:
    def setup_method(self):
        self.agent = EntityExtractorAgent()
        self.chunk = {"text": "Гарри Поттер живет в Лондоне.", "chunk_id": "c1", "file_name": "file.md"}

    def test_extract_entities_success(self, monkeypatch):
        response = {"response": json.dumps({"entities": [{"name": "Гарри Поттер", "type": "person", "description": "wizard", "mentions": ["Гарри Поттер"], "confidence": 0.9, "context": "Гарри Поттер живет"}]})}
        monkeypatch.setattr(self.agent, "_call_ollama_api", lambda prompt: response)
        entities = self.agent.extract_entities(self.chunk["text"], self.chunk)
        assert len(entities) == 1
        assert entities[0].name == "Гарри Поттер"
        assert entities[0].chunk_id == "c1"

    def test_extract_entities_empty_input(self):
        result = self.agent.extract_entities("  ", self.chunk)
        assert result == []

    def test_extract_entities_custom_types(self, monkeypatch):
        captured = {}

        def fake_call(prompt: str):
            captured["prompt"] = prompt
            return {"response": json.dumps({"entities": []})}

        monkeypatch.setattr(self.agent, "_call_ollama_api", fake_call)
        self.agent.extract_entities(self.chunk["text"], self.chunk, entity_types=["spell", "character"])
        assert "spell" in captured["prompt"] and "character" in captured["prompt"]

    def test_extract_entities_confidence_filtering(self, monkeypatch):
        resp = {"response": json.dumps({"entities": [
            {"name": "A", "type": "person", "confidence": 0.6, "mentions": ["A"], "context": "A"},
            {"name": "B", "type": "person", "confidence": 0.9, "mentions": ["B"], "context": "B"}]})}
        monkeypatch.setattr(self.agent, "_call_ollama_api", lambda prompt: resp)
        ents = self.agent.extract_entities(self.chunk["text"], self.chunk)
        assert len(ents) == 1
        assert ents[0].name == "B"

    def test_batch_processing(self, monkeypatch):
        responses = [
            {"response": json.dumps({"entities": [{"name": "A", "type": "person", "confidence": 0.9, "mentions": ["A"], "context": "A"}]})},
            {"response": json.dumps({"entities": [{"name": "B", "type": "person", "confidence": 0.9, "mentions": ["B"], "context": "B"}]})},
        ]
        calls = iter(responses)
        monkeypatch.setattr(self.agent, "_call_ollama_api", lambda prompt: next(calls))
        chunks = [self.chunk, {"text": "B", "chunk_id": "c2", "file_name": "file.md"}]
        res = self.agent.extract_entities_batch(chunks)
        assert len(res) == 2
        assert res[0][0].name == "A"
        assert res[1][0].name == "B"

    def test_ollama_connection_failure(self, monkeypatch):
        counter = {"i": 0}

        def fake_call(prompt: str):
            counter["i"] += 1
            if counter["i"] < 3:
                raise requests.ConnectionError("fail")
            return {"response": json.dumps({"entities": []})}

        monkeypatch.setattr(self.agent, "_call_ollama_api", fake_call)
        monkeypatch.setattr(self.agent, "base_delay", 0)
        self.agent.extract_entities(self.chunk["text"], self.chunk)
        assert counter["i"] == 3

    def test_invalid_json_response(self, monkeypatch):
        monkeypatch.setattr(self.agent, "_call_ollama_api", lambda prompt: {"response": "not json"})
        ents = self.agent.extract_entities(self.chunk["text"], self.chunk)
        assert ents == []

    def test_retry_logic(self, monkeypatch):
        counter = {"i": 0}

        def always_fail(prompt: str):
            counter["i"] += 1
            raise requests.RequestException("fail")

        monkeypatch.setattr(self.agent, "_call_ollama_api", always_fail)
        monkeypatch.setattr(self.agent, "base_delay", 0)
        result = self.agent.extract_entities(self.chunk["text"], self.chunk)
        assert result == []
        assert counter["i"] == self.agent.max_retries

    def test_prompt_generation(self):
        prompt = self.agent._build_extraction_prompt("text", ["person"])
        assert "person" in prompt and "text" in prompt

    def test_confidence_threshold(self, monkeypatch):
        resp = {"response": json.dumps({"entities": [
            {"name": "A", "type": "person", "confidence": 0.75, "mentions": ["A"], "context": "A"}
        ]})}
        monkeypatch.setattr(self.agent, "_call_ollama_api", lambda prompt: resp)
        ents = self.agent.extract_entities(self.chunk["text"], self.chunk, confidence_threshold=0.8)
        assert ents == []
        ents2 = self.agent.extract_entities(self.chunk["text"], self.chunk, confidence_threshold=0.7)
        assert len(ents2) == 1
