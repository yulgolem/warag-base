from __future__ import annotations

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from crewai import Agent, Task
import os

from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient
from src.utils.logging_utils import get_agent_logger, log_database_operation

class GraphCoordinatorAgent:
    """Agent responsible for managing knowledge graph and vector database operations."""
    
    def __init__(
        self, 
        neo4j_client: Neo4jClient,
        postgres_client: PostgresClient,
        embedding_model: str = "paraphrase-multilingual-mpnet-base-v2",
        similarity_threshold: float = 0.85,
        logger=None
    ):
        """Initialize the GraphCoordinatorAgent."""
        self.neo4j_client = neo4j_client
        self.postgres_client = postgres_client
        self.embedding_model_name = embedding_model
        self.similarity_threshold = similarity_threshold
        self.logger = logger or get_agent_logger()
        self._embedding_model = None  # Lazy initialization
        self.ollama_url = os.getenv("OLLAMA__BASE_URL", "http://ollama:11434")

    def _get_embedding_model(self):
        """Lazy load sentence-transformers model."""
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self._embedding_model = SentenceTransformer(self.embedding_model_name)
        return self._embedding_model

    def create_agent(self) -> Agent:
        """Create a CrewAI agent instance.
        
        Returns:
            Agent: Configured CrewAI agent for graph coordination
        """
        return Agent(
            role="Knowledge Graph Manager",
            goal="Store entities and relationships in graph database with deduplication",
            backstory="Expert in graph database operations and entity resolution",
            verbose=True,
            allow_delegation=False,
            memory=False,
            tools=[]
        )
        
    def store_knowledge(
        self, 
        entities: List[Entity], 
        relationships: List[Relationship],
        chunk_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store entities and relationships in the knowledge graph.
        
        Args:
            entities: List of entities to store
            relationships: List of relationships to store
            chunk_metadata: Metadata about the source chunk
            
        Returns:
            Dict containing statistics about the operation
        """
        stats = {
            "entities_created": 0,
            "entities_updated": 0,
            "entities_merged": 0,
            "relationships_created": 0,
            "relationships_updated": 0,
            "processing_time": 0
        }
        
        try:
            # 1. Deduplicate entities
            deduplicated_entities, merge_stats = self.deduplicate_entities(entities)
            stats.update(merge_stats)
            
            # 2. Store in Neo4j
            entity_stats = self._store_entities_neo4j(deduplicated_entities)
            stats.update(entity_stats)
            
            relationship_stats = self._store_relationships_neo4j(relationships)
            stats.update(relationship_stats)
            
            # 3. Store in PostgreSQL
            self._store_chunk_postgresql(chunk_metadata)
            self._store_entities_cache_postgresql(deduplicated_entities)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error storing knowledge: {str(e)}")
            raise 

    def deduplicate_entities(self, new_entities: List[Entity]) -> Tuple[List[Entity], Dict[str, Any]]:
        """Deduplicate entities using vector similarity + LLM confirmation.
        
        Args:
            new_entities: List of new entities to deduplicate
            
        Returns:
            Tuple of (deduplicated_entities, merge_statistics)
        """
        stats = {
            "entities_merged": 0,
            "llm_confirmations": 0,
            "similarity_checks": 0
        }
        
        # 1. Generate embeddings for new entities
        new_entity_embeddings = self._generate_embeddings(new_entities)
        
        # 2. Get existing entities by type and their embeddings
        existing_entity_map = {}
        for entity in new_entities:
            if entity.type not in existing_entity_map:
                existing_entity_map[entity.type] = self._get_existing_entities_by_type(entity.type)

        deduplicated_entities = []
        processed_entities = set()

        for new_entity in new_entities:
            if new_entity.name in processed_entities:
                continue

            # Find best match from existing entities
            best_match = None
            highest_similarity = -1.0
            
            existing_entities = existing_entity_map.get(new_entity.type, [])
            if existing_entities:
                new_embedding = new_entity_embeddings[new_entity.name]
                
                # Pre-fetch existing embeddings if not already present
                for ex_entity in existing_entities:
                    if 'embedding' not in ex_entity or ex_entity['embedding'] is None:
                        # This case should ideally not happen if DB is consistent
                        self.logger.warning(f"Entity '{ex_entity['name']}' in cache is missing an embedding. Generating one now.")
                        entity_obj = Entity(name=ex_entity['name'], type=ex_entity['type'], description=ex_entity.get('description', ''), confidence=ex_entity.get('confidence', 0), source_file=ex_entity.get('source_file', ''), chunk_id=ex_entity.get('chunk_id', ''), source_chunk='', context='')
                        ex_entity['embedding'] = self._generate_embeddings([entity_obj])[ex_entity['name']]

                existing_embeddings = [np.array(e['embedding']) for e in existing_entities if e.get('embedding') is not None]
                
                if existing_embeddings:
                    similarities = self._compute_similarity_matrix([new_embedding], existing_embeddings)[0]
                    
                    for i, similarity in enumerate(similarities):
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = existing_entities[i]

            if best_match and highest_similarity >= self.similarity_threshold:
                # Merge with the best match
                merged_entity = self._merge_entities(new_entity, best_match)
                deduplicated_entities.append(merged_entity)
                stats["entities_merged"] += 1
            elif best_match and 0.80 <= highest_similarity < self.similarity_threshold:
                # Borderline case: confirm with LLM
                stats["llm_confirmations"] += 1
                if self._confirm_merge_with_llm(new_entity, best_match, highest_similarity):
                    merged_entity = self._merge_entities(new_entity, best_match)
                    deduplicated_entities.append(merged_entity)
                    stats["entities_merged"] += 1
                else:
                    deduplicated_entities.append(new_entity)
            else:
                # No suitable match found
                deduplicated_entities.append(new_entity)
            
            processed_entities.add(new_entity.name)

        return deduplicated_entities, stats
        
    def _generate_embeddings(self, entities: List[Entity]) -> Dict[str, np.ndarray]:
        """Generate sentence-transformers embeddings for entity names + descriptions."""
        model = self._get_embedding_model()
        
        texts = [f"{entity.name} {entity.description or ''}".strip() for entity in entities]
        
        if not texts:
            return {}
            
        embeddings = model.encode(texts, convert_to_numpy=True)
        return {entity.name: emb for entity, emb in zip(entities, embeddings)}
        
    def _find_similar_entities(
        self, 
        new_entity: Entity, 
        existing_entities: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """Find existing entities similar to new entity.
        
        Args:
            new_entity: Entity to find matches for
            existing_entities: List of existing entities to check against
            
        Returns:
            List of (entity, similarity_score) tuples, sorted by similarity
        """
        if not existing_entities:
            return []
            
        # Get embedding for new entity
        new_embedding = self._generate_embeddings([new_entity])[new_entity.name]
        
        # Get embeddings for existing entities
        existing_embeddings = [np.array(e["embedding"]) for e in existing_entities]
        
        # Compute similarity matrix
        similarity_matrix = self._compute_similarity_matrix(
            [new_embedding], 
            existing_embeddings
        )[0]
        
        # Create (entity, similarity) pairs
        similar_entities = [
            (existing_entities[i], float(similarity_matrix[i]))
            for i in range(len(existing_entities))
            if similarity_matrix[i] >= 0.80  # Only consider potential matches
        ]
        
        # Sort by similarity score
        return sorted(similar_entities, key=lambda x: x[1], reverse=True)
        
    def _confirm_merge_with_llm(
        self, 
        entity1: Entity, 
        entity2_data: Dict, 
        similarity_score: float
    ) -> bool:
        """Use LLM to confirm if entities should be merged.
        
        Args:
            entity1: New entity
            entity2_data: Existing entity data
            similarity_score: Similarity score between entities
            
        Returns:
            True if entities should be merged, False otherwise
        """
        prompt = f"""Compare these two entities and determine if they refer to the same thing:

Entity 1:
Name: {entity1.name}
Type: {entity1.type}
Description: {entity1.description}

Entity 2:
Name: {entity2_data['name']}
Type: {entity2_data['type']}
Description: {entity2_data.get('description')}

Similarity score: {similarity_score:.2f}

Do these entities refer to the same thing? Answer with 'yes' or 'no' only."""

        # Call Saiga model through Ollama
        response = self._call_ollama_api(prompt, model="ilyagusev/saiga_llama3")
        
        # Parse response
        return response.strip().lower() == "yes"
        
    def _merge_entities(self, entity1: Entity, entity2_data: Dict) -> Entity:
        """Merge two entities, preserving all information.
        
        Args:
            entity1: New entity
            entity2_data: Existing entity data
            
        Returns:
            Merged entity
        """
        # Combine descriptions
        desc1 = entity1.description or ""
        desc2 = entity2_data["description"] or ""
        combined_desc = f"{desc1}; {desc2}".strip("; ")
        
        # Create merged entity
        return Entity(
            name=entity1.name,  # Keep new entity name
            type=entity1.type,
            description=combined_desc,
            confidence=max(entity1.confidence, entity2_data.get("confidence", 0.0)),
            source_file=entity1.source_file,
            chunk_id=entity1.chunk_id,
            source_chunk=entity1.source_chunk,
            context=entity1.context
        )
        
    def _call_ollama_api(self, prompt: str, model: str = "saiga") -> str:
        """Call Ollama API for LLM inference.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            
        Returns:
            Model response
        """
        import requests
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            self.logger.error(f"Ollama API error ({response.status_code}): {response.text}")
            raise Exception(f"Ollama API error: {response.text}")
            
        return response.json()["response"]
        
    def _compute_similarity_matrix(
        self, 
        new_embeddings: List[np.ndarray], 
        existing_embeddings: List[np.ndarray]
    ) -> np.ndarray:
        """Compute cosine similarity matrix between embeddings.
        
        Args:
            new_embeddings: List of new entity embeddings
            existing_embeddings: List of existing entity embeddings
            
        Returns:
            Similarity matrix
        """
        # Normalize vectors
        new_embeddings_np = np.array(new_embeddings)
        existing_embeddings_np = np.array(existing_embeddings)

        if new_embeddings_np.ndim == 1:
            new_embeddings_np = new_embeddings_np.reshape(1, -1)
        if existing_embeddings_np.ndim == 1:
            existing_embeddings_np = existing_embeddings_np.reshape(1, -1)
            
        new_norm = new_embeddings_np / np.linalg.norm(new_embeddings_np, axis=1, keepdims=True)
        existing_norm = existing_embeddings_np / np.linalg.norm(existing_embeddings_np, axis=1, keepdims=True)
        
        # Compute cosine similarity
        return np.dot(new_norm, existing_norm.T) 

    def _store_entities_neo4j(self, entities: List[Entity]) -> Dict[str, int]:
        """Store entities in Neo4j with merge logic.
        
        Args:
            entities: List of entities to store
            
        Returns:
            Dictionary with statistics about created/updated entities
        """
        stats = {
            "entities_created": 0,
            "entities_updated": 0
        }
        
        # Cypher query for entity creation/update
        query = """
        MERGE (e:Entity {name: $name, type: $type})
        ON CREATE SET 
            e.description = $description, 
            e.created_at = datetime(),
            e.source_files = [$source_file],
            e.chunk_ids = [$chunk_id]
        ON MATCH SET 
            e.description = CASE 
                WHEN e.description IS NULL THEN $description
                WHEN $description IS NOT NULL THEN e.description + '; ' + $description
                ELSE e.description
            END,
            e.updated_at = datetime(),
            e.source_files = CASE
                WHEN NOT $source_file IN e.source_files THEN e.source_files + $source_file
                ELSE e.source_files
            END,
            e.chunk_ids = CASE
                WHEN NOT $chunk_id IN e.chunk_ids THEN e.chunk_ids + $chunk_id  
                ELSE e.chunk_ids
            END
        RETURN e
        """
        
        # Process each entity
        for entity in entities:
            params = {
                "name": entity.name,
                "type": entity.type,
                "description": entity.description,
                "source_file": entity.source_file,
                "chunk_id": entity.chunk_id
            }
            
            result = self.neo4j_client.execute(query, params)
            
            # Check if entity was created or updated
            if result and len(result) > 0:
                if "created_at" in result[0]:
                    stats["entities_created"] += 1
                else:
                    stats["entities_updated"] += 1
                    
        return stats
        
    def _store_relationships_neo4j(self, relationships: List[Relationship]) -> Dict[str, int]:
        """Store relationships in Neo4j.
        
        Args:
            relationships: List of relationships to store
            
        Returns:
            Dictionary with statistics about created/updated relationships
        """
        stats = {
            "relationships_created": 0,
            "relationships_updated": 0
        }
        
        # Cypher query for relationship creation/update
        query = """
        MATCH (a:Entity {name: $source_entity})
        MATCH (b:Entity {name: $target_entity})
        MERGE (a)-[r:RELATED {type: $relation_type}]->(b)
        ON CREATE SET 
            r.description = $description, 
            r.confidence = $confidence,
            r.created_at = datetime(),
            r.source_text = $source_text
        ON MATCH SET
            r.confidence = CASE
                WHEN $confidence > r.confidence THEN $confidence
                ELSE r.confidence
            END,
            r.updated_at = datetime()
        RETURN r
        """
        
        # Process each relationship
        for rel in relationships:
            params = {
                "source_entity": rel.source_entity,
                "target_entity": rel.target_entity,
                "relation_type": rel.relation_type,
                "description": rel.description,
                "confidence": rel.confidence,
                "source_text": rel.source_text
            }
            
            result = self.neo4j_client.execute(query, params)
            
            # Check if relationship was created or updated
            if result and len(result) > 0:
                if "created_at" in result[0]:
                    stats["relationships_created"] += 1
                else:
                    stats["relationships_updated"] += 1
                    
        return stats
        
    def _store_chunk_postgresql(self, chunk_metadata: Dict[str, Any]) -> bool:
        """Store text chunk with embeddings in PostgreSQL.
        
        Args:
            chunk_metadata: Metadata about the chunk to store
            
        Returns:
            True if successful, False otherwise
        """
        text = chunk_metadata.get("text")
        if not text:
            self.logger.error("No text found in chunk metadata to store.")
            return False

        try:
            # Generate embedding for the chunk text
            chunk_entity = Entity(name="chunk", description=text, type="chunk", confidence=1.0, source_file=chunk_metadata.get('file_name', ''), chunk_id=chunk_metadata.get('chunk_id', ''), source_chunk=text, context='')
            embedding = list(self._generate_embeddings([chunk_entity]).values())[0]

            query = """
            INSERT INTO chunks (chunk_id, source_file, text, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                text = EXCLUDED.text,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP;
            """
            params = (
                chunk_metadata.get('chunk_id'),
                chunk_metadata.get('file_name'),
                text,
                embedding.tolist(),
                str(chunk_metadata) # Store metadata as a string
            )
            self.postgres_client.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"Error storing chunk in PostgreSQL: {e}")
            return False
            
    def _store_entities_cache_postgresql(self, entities: List[Entity]) -> bool:
        """Store entities with embeddings for deduplication.
        
        Args:
            entities: List of entities to store
            
        Returns:
            True if successful, False otherwise
        """
        if not entities:
            return True # Nothing to store

        try:
            embeddings_dict = self._generate_embeddings(entities)
            
            query = """
            INSERT INTO entities_cache (name, type, description, embedding, source_file, chunk_id, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name, type) DO UPDATE SET
                description = EXCLUDED.description,
                embedding = EXCLUDED.embedding,
                source_file = EXCLUDED.source_file,
                chunk_id = EXCLUDED.chunk_id,
                confidence = EXCLUDED.confidence,
                updated_at = CURRENT_TIMESTAMP;
            """
            
            for entity in entities:
                if entity.name in embeddings_dict:
                    params = (
                        entity.name,
                        entity.type,
                        entity.description,
                        embeddings_dict[entity.name].tolist(),
                        entity.source_file,
                        entity.chunk_id,
                        entity.confidence
                    )
                    self.postgres_client.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"Error storing entities in cache: {e}")
            return False
            
    def _get_existing_entities_by_type(self, entity_type: str) -> List[Dict]:
        """Retrieve existing entities from PostgreSQL for deduplication.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of entity dictionaries with embeddings
        """
        query = """
        SELECT 
            name,
            type,
            description,
            embedding,
            source_file,
            confidence
        FROM entities_cache 
        WHERE type = %s
        ORDER BY created_at DESC
        """
        
        try:
            results = self.postgres_client.execute(query, (entity_type,))
            self.logger.info(f"Retrieved {len(results)} entities of type '{entity_type}' from cache.")
            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "description": row[2],
                    "embedding": np.frombuffer(row[3], dtype=np.float32) if isinstance(row[3], bytes) else (np.array(row[3]) if row[3] is not None else None),
                    "source_file": row[4],
                    "confidence": row[5]
                }
                for row in results
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving entities by type '{entity_type}': {str(e)}")
            return [] 