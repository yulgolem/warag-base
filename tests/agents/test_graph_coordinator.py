import pytest
import numpy as np
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from src.agents.graph_coordinator import GraphCoordinatorAgent
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient

@pytest.fixture
def mock_neo4j():
    return Mock(spec=Neo4jClient)

@pytest.fixture
def mock_postgres():
    return Mock(spec=PostgresClient)

@pytest.fixture
def graph_coordinator(mock_neo4j, mock_postgres):
    return GraphCoordinatorAgent(
        neo4j_client=mock_neo4j,
        postgres_client=mock_postgres,
        embedding_model_url="http://test:11434",
        similarity_threshold=0.85
    )

@pytest.fixture
def sample_entities() -> List[Entity]:
    return [
        Entity(
            name="Test Entity 1",
            type="Character",
            description="A test character",
            confidence=0.9,
            source_file="test.md",
            chunk_id="chunk1",
            source_chunk="Test chunk 1",
            context="Test context 1"
        ),
        Entity(
            name="Test Entity 2",
            type="Location",
            description="A test location",
            confidence=0.8,
            source_file="test.md",
            chunk_id="chunk1",
            source_chunk="Test chunk 1",
            context="Test context 1"
        )
    ]

@pytest.fixture
def sample_relationships() -> List[Relationship]:
    return [
        Relationship(
            source_entity="Test Entity 1",
            target_entity="Test Entity 2",
            relation_type="LIVES_IN",
            description="Character lives in location",
            confidence=0.9,
            source_text="Test Entity 1 lives in Test Entity 2"
        )
    ]

class TestGraphCoordinatorAgent:
    def test_create_agent(self, graph_coordinator):
        agent = graph_coordinator.create_agent()
        assert agent.role == "Knowledge Graph Manager"
        assert agent.goal == "Store entities and relationships in graph database with deduplication"
        assert agent.backstory == "Expert in graph database operations and entity resolution"

    @patch('src.agents.graph_coordinator.GraphCoordinatorAgent._call_frida_api')
    def test_deduplicate_entities_no_matches(self, mock_frida, graph_coordinator, sample_entities):
        # Mock FRIDA API response
        mock_frida.return_value = [np.random.rand(384) for _ in sample_entities]
        
        # Mock PostgreSQL response - no existing entities
        graph_coordinator.postgres.execute.return_value = []
        
        # Test deduplication
        deduplicated, stats = graph_coordinator.deduplicate_entities(sample_entities)
        
        assert len(deduplicated) == len(sample_entities)
        assert stats["entities_merged"] == 0
        assert stats["llm_confirmations"] == 0
        assert stats["similarity_checks"] == 0

    @patch('src.agents.graph_coordinator.GraphCoordinatorAgent._call_frida_api')
    @patch('src.agents.graph_coordinator.GraphCoordinatorAgent._confirm_merge_with_llm')
    def test_deduplicate_entities_with_merge(self, mock_llm, mock_frida, graph_coordinator, sample_entities):
        # Mock FRIDA API response
        mock_frida.return_value = [np.random.rand(384) for _ in sample_entities]
        
        # Mock existing entity with high similarity
        existing_entity = {
            "name": "Test Entity 1",
            "type": "Character",
            "description": "Another description",
            "embedding": np.random.rand(384),
            "source_file": "old.md",
            "confidence": 0.7
        }
        graph_coordinator.postgres.execute.return_value = [
            (existing_entity["name"], existing_entity["type"], existing_entity["description"],
             existing_entity["embedding"].tolist(), existing_entity["source_file"], existing_entity["confidence"])
        ]
        
        # Mock LLM confirmation
        mock_llm.return_value = True
        
        # Test deduplication
        deduplicated, stats = graph_coordinator.deduplicate_entities(sample_entities)
        
        assert len(deduplicated) == len(sample_entities)
        assert stats["entities_merged"] > 0
        assert any("Another description" in e.description for e in deduplicated)

    def test_store_entities_neo4j(self, graph_coordinator, sample_entities):
        # Mock Neo4j response
        graph_coordinator.neo4j.execute.return_value = [
            {"created_at": "2024-01-01"}
        ]
        
        # Test storing entities
        stats = graph_coordinator._store_entities_neo4j(sample_entities)
        
        assert stats["entities_created"] == len(sample_entities)
        assert stats["entities_updated"] == 0
        assert graph_coordinator.neo4j.execute.call_count == len(sample_entities)

    def test_store_relationships_neo4j(self, graph_coordinator, sample_relationships):
        # Mock Neo4j response
        graph_coordinator.neo4j.execute.return_value = [
            {"created_at": "2024-01-01"}
        ]
        
        # Test storing relationships
        stats = graph_coordinator._store_relationships_neo4j(sample_relationships)
        
        assert stats["relationships_created"] == len(sample_relationships)
        assert stats["relationships_updated"] == 0
        assert graph_coordinator.neo4j.execute.call_count == len(sample_relationships)

    @patch('src.agents.graph_coordinator.GraphCoordinatorAgent._call_frida_api')
    def test_store_chunk_postgresql(self, mock_frida, graph_coordinator):
        # Mock FRIDA API response
        mock_frida.return_value = [np.random.rand(384)]
        
        # Test storing chunk
        chunk_metadata = {
            "chunk_id": "test_chunk",
            "source_file": "test.md",
            "text": "Test text",
            "metadata": {"key": "value"}
        }
        
        result = graph_coordinator._store_chunk_postgresql(chunk_metadata)
        
        assert result is True
        assert graph_coordinator.postgres.execute.call_count == 1

    @patch('src.agents.graph_coordinator.GraphCoordinatorAgent._call_frida_api')
    def test_store_entities_cache_postgresql(self, mock_frida, graph_coordinator, sample_entities):
        # Mock FRIDA API response
        mock_frida.return_value = [np.random.rand(384) for _ in sample_entities]
        
        # Test storing entities cache
        result = graph_coordinator._store_entities_cache_postgresql(sample_entities)
        
        assert result is True
        assert graph_coordinator.postgres.execute.call_count == len(sample_entities)

    def test_get_existing_entities_by_type(self, graph_coordinator):
        # Mock PostgreSQL response
        mock_entity = {
            "name": "Test Entity",
            "type": "Character",
            "description": "Test description",
            "embedding": np.random.rand(384).tolist(),
            "source_file": "test.md",
            "confidence": 0.9
        }
        graph_coordinator.postgres.execute.return_value = [
            (mock_entity["name"], mock_entity["type"], mock_entity["description"],
             mock_entity["embedding"], mock_entity["source_file"], mock_entity["confidence"])
        ]
        
        # Test retrieving entities
        entities = graph_coordinator._get_existing_entities_by_type("Character")
        
        assert len(entities) == 1
        assert entities[0]["name"] == mock_entity["name"]
        assert entities[0]["type"] == mock_entity["type"]
        assert isinstance(entities[0]["embedding"], np.ndarray) 