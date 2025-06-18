from unittest.mock import patch, Mock
import pytest
from datetime import datetime
from src.agents.graph_coordinator import GraphCoordinatorAgent
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient

@pytest.fixture
def graph_coordinator():
    neo4j_client = Mock(spec=Neo4jClient)
    postgres_client = Mock(spec=PostgresClient)
    postgres_client.execute.return_value = []  # Возвращаем пустой список для всех запросов
    coordinator = GraphCoordinatorAgent(
        neo4j_client=neo4j_client,
        postgres_client=postgres_client
    )
    return coordinator

@pytest.fixture
def sample_entities():
    return [
        Entity(
            name="Гарри Поттер",
            type="person",
            description="Главный герой серии книг о Гарри Поттере",
            confidence=0.9,
            source_file="test.md",
            chunk_id="c1",
            source_chunk="Гарри Поттер учился в Хогвартсе.",
            context="Гарри Поттер - главный герой серии книг о Гарри Поттере. Он учился в Хогвартсе."
        ),
        Entity(
            name="Хогвартс",
            type="location",
            description="Школа чародейства и волшебства",
            confidence=0.9,
            source_file="test.md",
            chunk_id="c1",
            source_chunk="Гарри Поттер учился в Хогвартсе.",
            context="Хогвартс - школа чародейства и волшебства, где учился Гарри Поттер."
        )
    ]

@pytest.fixture
def sample_relationships():
    return [
        Relationship(
            source_entity="Гарри Поттер",
            target_entity="Хогвартс",
            relation_type="STUDIED_AT",
            description="Гарри Поттер учился в Хогвартсе",
            confidence=0.9,
            source_text="Гарри Поттер учился в Хогвартсе."
        )
    ]

@pytest.fixture
def chunk_metadata():
    return {
        "chunk_id": "c1",
        "file_name": "test.md",
        "text": "Гарри Поттер учился в Хогвартсе."
    }

def test_store_relationships_neo4j(graph_coordinator, sample_relationships):
    # Mock Neo4j response: возвращаем структуру с ключом "r"
    graph_coordinator.neo4j.execute.return_value = [{"r": {"created_at": "2024-01-01", "type": sample_relationships[0].relation_type}}]
    
    # Test storing relationships
    stats = graph_coordinator._store_relationships_neo4j(sample_relationships)
    
    # Verify results
    assert stats["relationships_created"] == 1
    assert stats["relationships_updated"] == 0
    assert graph_coordinator.neo4j.execute.call_count == 1

@patch('requests.post')
def test_store_knowledge_success(mock_post, graph_coordinator, sample_entities, sample_relationships, chunk_metadata):
    # Mock embedding response
    mock_post.return_value.json.return_value = {
        "embedding": [0.1, 0.2, 0.3]
    }
    mock_post.return_value.raise_for_status = Mock()

    # Side effect для мока Neo4j: возвращаем разную структуру для сущностей и связей
    def neo4j_execute_side_effect(query, params):
        if "MERGE (e:Entity" in query:
            return [{"e": {"created_at": "2024-01-01", "type": params["type"]}}]
        if "MERGE (r:" in query or "MERGE (source)-[r:" in query:
            return [{"r": {"created_at": "2024-01-01", "type": params.get("relation_type", "STUDIED_AT")}}]
        return []
    graph_coordinator.neo4j.execute.side_effect = neo4j_execute_side_effect

    # Test storing knowledge
    result = graph_coordinator.store_knowledge(sample_entities, sample_relationships, chunk_metadata)

    # Verify results
    assert result["entities_created"] == len(sample_entities)
    assert result["relationships_created"] == len(sample_relationships)
    assert result["errors"] == [] 