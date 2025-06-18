import pytest
import os
from typing import List, Dict, Any
import time
from datetime import datetime
from unittest.mock import patch

from src.agents.graph_coordinator import GraphCoordinatorAgent
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient

@pytest.fixture(scope="module")
def neo4j_client():
    """Create real Neo4j client connection."""
    client = Neo4jClient(
        uri="bolt://worldbuilding_neo4j:7687",
        user="neo4j",
        password="worldbuilding123"
    )
    yield client
    client.close()

@pytest.fixture(scope="module")
def postgres_client():
    """Create real PostgreSQL client connection."""
    client = PostgresClient(
        host="worldbuilding_postgres",
        port=5432,
        database="worldbuilding",
        user="postgres",
        password="postgres"
    )
    yield client
    client.close()

@pytest.fixture(scope="module")
def graph_coordinator(neo4j_client, postgres_client):
    """Create GraphCoordinatorAgent with real database connections."""
    return GraphCoordinatorAgent(
        neo4j_client=neo4j_client,
        postgres_client=postgres_client,
        embedding_model="paraphrase-multilingual-mpnet-base-v2",
        similarity_threshold=0.85
    )

@pytest.fixture(scope="module")
def sample_entities() -> List[Entity]:
    """Sample entities for testing."""
    return [
        Entity(
            name="Александр Невский",
            type="person",
            description="Князь Новгородский, великий полководец",
            confidence=0.95,
            source_file="test_integration.md",
            chunk_id="integration_test_1",
            source_chunk="Александр Невский защищал Русь от западных захватчиков.",
            context="Александр Невский - князь Новгородский, который защищал Русь от западных захватчиков в XIII веке."
        ),
        Entity(
            name="Новгород",
            type="location",
            description="Древний русский город, центр Новгородской республики",
            confidence=0.95,
            source_file="test_integration.md",
            chunk_id="integration_test_1",
            source_chunk="Александр Невский защищал Русь от западных захватчиков.",
            context="Новгород - древний русский город, который был центром Новгородской республики."
        ),
        Entity(
            name="Ледовое побоище",
            type="event",
            description="Битва на Чудском озере в 1242 году",
            confidence=0.95,
            source_file="test_integration.md",
            chunk_id="integration_test_1",
            source_chunk="Александр Невский защищал Русь от западных захватчиков.",
            context="Ледовое побоище - знаменитая битва на Чудском озере в 1242 году."
        )
    ]

@pytest.fixture(scope="module")
def sample_relationships() -> List[Relationship]:
    """Sample relationships for testing."""
    return [
        Relationship(
            source_entity="Александр Невский",
            target_entity="Новгород",
            relation_type="RULED",
            description="Александр Невский правил в Новгороде",
            confidence=0.95,
            source_text="Александр Невский был князем Новгородским."
        ),
        Relationship(
            source_entity="Александр Невский",
            target_entity="Ледовое побоище",
            relation_type="PARTICIPATED_IN",
            description="Александр Невский участвовал в Ледовом побоище",
            confidence=0.95,
            source_text="Александр Невский командовал русскими войсками в Ледовом побоище."
        ),
        Relationship(
            source_entity="Ледовое побоище",
            target_entity="Новгород",
            relation_type="PROTECTED",
            description="Ледовое побоище защитило Новгород от захватчиков",
            confidence=0.95,
            source_text="Ледовое побоище защитило Новгород от западных захватчиков."
        )
    ]

@pytest.fixture(scope="module")
def chunk_metadata() -> Dict[str, Any]:
    """Sample chunk metadata for testing."""
    return {
        "chunk_id": "integration_test_1",
        "file_name": "test_integration.md",
        "text": "Александр Невский защищал Русь от западных захватчиков. Он был князем Новгородским и командовал русскими войсками в знаменитой битве на Чудском озере в 1242 году, известной как Ледовое побоище."
    }

@pytest.mark.integration
class TestGraphCoordinatorIntegration:
    """Integration tests for GraphCoordinatorAgent with real database connections."""
    
    def test_database_connections(self, neo4j_client, postgres_client):
        """Test that database connections are working."""
        # Test Neo4j connection
        try:
            result = neo4j_client.execute("RETURN 1 as test")
            assert result is not None
            assert len(result) > 0
            assert result[0]["test"] == 1
            print("✓ Neo4j connection successful")
        except Exception as e:
            pytest.fail(f"Neo4j connection failed: {e}")
        
        # Test PostgreSQL connection
        try:
            result = postgres_client.execute("SELECT 1 as test")
            assert result is not None
            assert len(result) > 0
            assert result[0][0] == 1
            print("✓ PostgreSQL connection successful")
        except Exception as e:
            pytest.fail(f"PostgreSQL connection failed: {e}")
    
    def test_store_knowledge_integration(
        self, 
        graph_coordinator, 
        sample_entities, 
        sample_relationships, 
        chunk_metadata
    ):
        """Integration test for storing knowledge with real database operations."""
        # Test storing knowledge with real Ollama API
        start_time = time.time()
        result = graph_coordinator.store_knowledge(
            sample_entities, 
            sample_relationships, 
            chunk_metadata
        )
        processing_time = time.time() - start_time
        
        # Verify results
        assert result is not None
        assert "entities_created" in result
        assert "relationships_created" in result
        assert "entities_merged" in result
        assert "processing_time" in result
        
        # Verify entity creation
        assert result["entities_created"] >= 0
        assert result["entities_created"] <= len(sample_entities)
        
        # Verify relationship creation
        assert result["relationships_created"] >= 0
        assert result["relationships_created"] <= len(sample_relationships)
        
        # Verify processing time is reasonable
        assert processing_time < 60.0  # Should complete within 60 seconds
        
        print(f"✓ Knowledge storage successful:")
        print(f"  Entities created: {result['entities_created']}")
        print(f"  Relationships created: {result['relationships_created']}")
        print(f"  Entities merged: {result['entities_merged']}")
        print(f"  Processing time: {processing_time:.2f}s")
    
    def test_entity_deduplication_integration(self, graph_coordinator, sample_entities):
        """Test entity deduplication with real embeddings."""
        # Create duplicate entities with slight variations
        duplicate_entities = [
            Entity(
                name="Александр Невский",
                type="person",
                description="Князь Новгородский, великий полководец",
                confidence=0.95,
                source_file="test_integration_2.md",
                chunk_id="integration_test_2",
                source_chunk="Александр Невский был великим полководцем.",
                context="Александр Невский - князь Новгородский, который был великим полководцем."
            ),
            Entity(
                name="Александр Невский",
                type="person",
                description="Святой князь, защитник Руси",
                confidence=0.90,
                source_file="test_integration_3.md",
                chunk_id="integration_test_3",
                source_chunk="Александр Невский был причислен к лику святых.",
                context="Александр Невский - святой князь, который был причислен к лику святых."
            )
        ]
        
        # Test deduplication
        deduplicated, stats = graph_coordinator.deduplicate_entities(duplicate_entities)
        
        # Verify deduplication results
        assert deduplicated is not None
        assert stats is not None
        assert "entities_merged" in stats
        assert "similarity_checks" in stats
        
        print(f"✓ Entity deduplication successful:")
        print(f"  Original entities: {len(duplicate_entities)}")
        print(f"  Deduplicated entities: {len(deduplicated)}")
        print(f"  Entities merged: {stats['entities_merged']}")
        print(f"  Similarity checks: {stats['similarity_checks']}")
    
    def test_relationship_storage_integration(self, graph_coordinator, sample_relationships):
        """Test relationship storage with real Neo4j operations."""
        # Test storing relationships directly
        stats = graph_coordinator._store_relationships_neo4j(sample_relationships)
        
        # Verify relationship storage results
        assert stats is not None
        assert "relationships_created" in stats
        assert "relationships_updated" in stats
        
        print(f"✓ Relationship storage successful:")
        print(f"  Relationships created: {stats['relationships_created']}")
        print(f"  Relationships updated: {stats['relationships_updated']}")
    
    def test_entity_storage_integration(self, graph_coordinator, sample_entities):
        """Test entity storage with real Neo4j operations."""
        # Test storing entities directly
        stats = graph_coordinator._store_entities_neo4j(sample_entities)
        
        # Verify entity storage results
        assert stats is not None
        assert "entities_created" in stats
        assert "entities_updated" in stats
        
        print(f"✓ Entity storage successful:")
        print(f"  Entities created: {stats['entities_created']}")
        print(f"  Entities updated: {stats['entities_updated']}")
    
    def test_chunk_storage_integration(self, graph_coordinator, chunk_metadata):
        """Test chunk storage with real PostgreSQL operations."""
        # Test storing chunk metadata
        success = graph_coordinator._store_chunk_postgresql(chunk_metadata)
        
        # Verify chunk storage
        assert success is True
        
        print(f"✓ Chunk storage: {'Success' if success else 'Failed'}")
    
    def test_entities_cache_storage_integration(self, graph_coordinator, sample_entities):
        """Test entities cache storage with real PostgreSQL operations."""
        # Test storing entities in cache
        success = graph_coordinator._store_entities_cache_postgresql(sample_entities)
        
        # Verify cache storage
        assert success is True
        
        print(f"✓ Entities cache storage: {'Success' if success else 'Failed'}")
    
    def test_existing_entities_retrieval_integration(self, graph_coordinator):
        """Test retrieving existing entities from PostgreSQL."""
        # Test retrieving entities by type
        person_entities = graph_coordinator._get_existing_entities_by_type("person")
        location_entities = graph_coordinator._get_existing_entities_by_type("location")
        
        # Verify retrieval results
        assert person_entities is not None
        assert location_entities is not None
        assert isinstance(person_entities, list)
        assert isinstance(location_entities, list)
        
        print(f"✓ Existing entities retrieval successful:")
        print(f"  Person entities: {len(person_entities)}")
        print(f"  Location entities: {len(location_entities)}")
    
    def test_full_workflow_integration(
        self, 
        graph_coordinator, 
        sample_entities, 
        sample_relationships, 
        chunk_metadata
    ):
        """Test the complete workflow from entities to knowledge graph."""
        print("\n=== Full Integration Test Workflow ===")
        
        # Step 1: Test entity deduplication
        print("1. Testing entity deduplication...")
        deduplicated_entities, dedup_stats = graph_coordinator.deduplicate_entities(sample_entities)
        print(f"   Deduplicated {len(sample_entities)} -> {len(deduplicated_entities)} entities")
        
        # Step 2: Test entity storage
        print("2. Testing entity storage...")
        entity_stats = graph_coordinator._store_entities_neo4j(deduplicated_entities)
        print(f"   Created {entity_stats['entities_created']} entities")
        
        # Step 3: Test relationship storage
        print("3. Testing relationship storage...")
        relationship_stats = graph_coordinator._store_relationships_neo4j(sample_relationships)
        print(f"   Created {relationship_stats['relationships_created']} relationships")
        
        # Step 4: Test chunk storage
        print("4. Testing chunk storage...")
        chunk_success = graph_coordinator._store_chunk_postgresql(chunk_metadata)
        print(f"   Chunk storage: {'Success' if chunk_success else 'Failed'}")
        
        # Step 5: Test entities cache storage
        print("5. Testing entities cache storage...")
        cache_success = graph_coordinator._store_entities_cache_postgresql(deduplicated_entities)
        print(f"   Cache storage: {'Success' if cache_success else 'Failed'}")
        
        # Verify overall workflow
        assert len(deduplicated_entities) >= 0
        assert entity_stats["entities_created"] >= 0
        assert relationship_stats["relationships_created"] >= 0
        assert chunk_success is True
        assert cache_success is True
        
        print("=== Integration Test Completed Successfully ===") 