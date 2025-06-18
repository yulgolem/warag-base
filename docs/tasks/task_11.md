# Task 11: Graph Coordinator Agent

## ЦЕЛЬ
Создать CrewAI агент для управления графом знаний (Neo4j) и векторной базой данных (PostgreSQL), включая дедупликацию сущностей и сохранение результатов обработки.

## ФАЙЛ
`src/agents/graph_coordinator.py`

## ОСНОВНЫЕ ТРЕБОВАНИЯ

### 1. CrewAI Agent Integration
- Role: "Knowledge Graph Manager"
- Goal: "Store entities and relationships in graph database with deduplication"
- Backstory: "Expert in graph database operations and entity resolution"

### 2. Dual Database Management
- **Neo4j**: сущности (nodes) + отношения (edges)
- **PostgreSQL**: текстовые чанки + векторные эмбеддинги
- **FRIDA embeddings** для семантического поиска
- Transactional operations с rollback capability

### 3. Entity Deduplication
- **Vector similarity**: FRIDA embeddings comparison
- **Similarity threshold**: 0.85 (настраиваемый)
- **LLM confirmation**: для borderline cases (0.80-0.90)
- **Merge strategy**: combine descriptions, preserve all sources

### 4. Statistics & Monitoring
- Entities created/updated/merged
- Relationships created
- Processing time metrics
- Database operation counts

## АЛГОРИТМ РЕАЛИЗАЦИИ

### Шаг 1: Agent Class Structure
```python
from crewai import Agent, Task
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient
from src.utils.logging_utils import get_agent_logger, log_database_operation

class GraphCoordinatorAgent:
    def __init__(
        self, 
        neo4j_client: Neo4jClient,
        postgres_client: PostgresClient,
        embedding_model_url: str = "http://ollama:11434",
        similarity_threshold: float = 0.85
    ):
        self.neo4j = neo4j_client
        self.postgres = postgres_client
        self.embedding_url = embedding_model_url
        self.similarity_threshold = similarity_threshold
        self.logger = get_agent_logger()
        
    def create_agent(self) -> Agent:
        # CrewAI Agent creation
        
    def store_knowledge(
        self, 
        entities: List[Entity], 
        relationships: List[Relationship],
        chunk_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Main orchestration method
        
    def store_knowledge_batch(
        self,
        entities_batches: List[List[Entity]],
        relationships_batches: List[List[Relationship]], 
        chunks_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # Batch processing multiple chunks
```

### Шаг 2: Entity Deduplication Core
```python
def deduplicate_entities(self, new_entities: List[Entity]) -> Tuple[List[Entity], Dict[str, Any]]:
    """
    Deduplicate entities using vector similarity + LLM confirmation
    Returns: (deduplicated_entities, merge_statistics)
    """
    
    # Algorithm:
    # 1. Generate embeddings для new entities
    # 2. Найти existing entities того же типа из PostgreSQL  
    # 3. Compute similarity matrix
    # 4. Identify candidates (similarity > threshold)
    # 5. LLM confirmation для borderline cases
    # 6. Merge duplicate entities
    # 7. Return deduplicated list + stats

def _generate_embeddings(self, entities: List[Entity]) -> Dict[str, np.ndarray]:
    """Generate FRIDA embeddings for entity names + descriptions"""
    
    # 1. Prepare text для каждой entity (name + description)
    # 2. Call FRIDA model через Ollama API
    # 3. Return dictionary {entity.name: embedding_vector}

def _find_similar_entities(
    self, 
    new_entity: Entity, 
    existing_entities: List[Dict]
) -> List[Tuple[Dict, float]]:
    """Find existing entities similar to new entity"""
    
    # 1. Filter existing entities по типу
    # 2. Compute cosine similarity с new entity embedding
    # 3. Return candidates выше similarity threshold
    # 4. Sort по similarity score

def _confirm_merge_with_llm(
    self, 
    entity1: Entity, 
    entity2_data: Dict, 
    similarity_score: float
) -> bool:
    """Use LLM to confirm if entities should be merged"""
    
    # 1. Build prompt для LLM comparison
    # 2. Call Saiga model
    # 3. Parse yes/no response
    # 4. Return merge decision
```

### Шаг 3: Neo4j Graph Operations
```python
# Cypher queries constants
CREATE_ENTITY_QUERY = """
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

CREATE_RELATIONSHIP_QUERY = """
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

def _store_entities_neo4j(self, entities: List[Entity]) -> Dict[str, int]:
    """Store entities in Neo4j with merge logic"""
    
    # 1. Batch создание entities через транзакцию
    # 2. Handle duplicates через ON MATCH logic
    # 3. Track создание vs updates
    # 4. Return statistics

def _store_relationships_neo4j(self, relationships: List[Relationship]) -> Dict[str, int]:
    """Store relationships in Neo4j"""
    
    # 1. Проверить что source/target entities существуют
    # 2. Создать relationships через MERGE
    # 3. Handle confidence updates
    # 4. Return statistics
```

### Шаг 4: PostgreSQL Vector Operations
```python
def _store_chunk_postgresql(self, chunk_metadata: Dict[str, Any]) -> bool:
    """Store text chunk with embeddings in PostgreSQL"""
    
    # 1. Generate embedding для chunk text
    # 2. Insert в chunks table
    # 3. Handle conflicts (ON CONFLICT DO UPDATE)
    # 4. Return success status

def _store_entities_cache_postgresql(self, entities: List[Entity]) -> bool:
    """Store entities with embeddings for deduplication"""
    
    # 1. Generate embeddings для entity names
    # 2. Insert в entities_cache table
    # 3. Update existing entities если нужно
    # 4. Return success status

def _get_existing_entities_by_type(self, entity_type: str) -> List[Dict]:
    """Retrieve existing entities from PostgreSQL for deduplication"""
    
    # SQL query to get entities с embeddings
    query = """
    SELECT name, type, description, embedding, source_file
    FROM entities_cache 
    WHERE type = %s
    ORDER BY created_at DESC
    """
```

### Шаг 5: FRIDA Embeddings Integration
```python
def _call_frida_api(self, texts: List[str]) -> List[np.ndarray]:
    """Generate embeddings using FRIDA model via Ollama"""
    
    # 1. Prepare batch request для FRIDA
    # 2. Call Ollama API
    # 3. Parse embedding responses
    # 4. Convert to numpy arrays
    # 5. Handle API errors gracefully

def _compute_similarity_matrix(
    self, 
    new_embeddings: List[np.ndarray], 
    existing_embeddings: List[np.ndarray]
) -> np.ndarray:
    """Compute cosine similarity matrix between embeddings"""
    
    # 1. Normalize vectors
    # 2. Compute cosine similarity
    # 3. Return similarity matrix
```

## LLM MERGE CONFIRMATION

### Prompt Template для Saiga
```python
MERGE_CONFIRMATION_PROMPT = """### Задача: Определить, являются ли две сущности одинаковыми.

### Сущность 1:
Название: {entity1_name}
Тип: {entity1_type}
Описание: {entity1_description}
Источник: {entity1_source}

### Сущность 2:
Название: {entity2_name} 
Тип: {entity2_type}
Описание: {entity2_description}
Источник: {entity2_source}

### Векторное сходство: {similarity_score:.3f}

### Инструкции:
1. Сравните названия сущностей
2. Учтите контекст и описания
3. Определите, это одна и та же сущность или разные
4. Учтите возможные вариации написания

### Формат ответа (только JSON):
{{
  "should_merge": true/false,
  "reason": "краткое_объяснение_решения"
}}

### Ответ:"""
```

## TRANSACTION MANAGEMENT

```python
def store_knowledge(self, entities, relationships, chunk_metadata):
    """Main method with full transaction support"""
    
    start_time = time.time()
    stats = {
        "entities_processed": 0,
        "entities_created": 0,
        "entities_merged": 0,
        "relationships_created": 0,
        "chunks_stored": 0,
        "processing_time": 0,
        "errors": []
    }
    
    try:
        # 1. Begin transactions в обеих БД
        
        # 2. Store chunk в PostgreSQL first
        self._store_chunk_postgresql(chunk_metadata)
        stats["chunks_stored"] = 1
        
        # 3. Deduplicate entities
        dedupe_entities, dedupe_stats = self.deduplicate_entities(entities)
        stats.update(dedupe_stats)
        
        # 4. Store entities в Neo4j
        entity_stats = self._store_entities_neo4j(dedupe_entities)
        stats.update(entity_stats)
        
        # 5. Store entities cache в PostgreSQL
        self._store_entities_cache_postgresql(dedupe_entities)
        
        # 6. Store relationships в Neo4j
        rel_stats = self._store_relationships_neo4j(relationships)
        stats.update(rel_stats)
        
        # 7. Commit transactions
        
        stats["processing_time"] = time.time() - start_time
        self._log_processing_stats(stats)
        
        return stats
        
    except Exception as e:
        # Rollback both databases
        self.logger.error(f"Failed to store knowledge: {e}")
        stats["errors"].append(str(e))
        # Rollback logic
        raise
```

## PERFORMANCE OPTIMIZATION

### Batch Operations
```python
def store_knowledge_batch(self, entities_batches, relationships_batches, chunks_metadata):
    """Optimized batch processing"""
    
    # 1. Process все chunks в single transaction где возможно
    # 2. Batch entity deduplication
    # 3. Bulk inserts в PostgreSQL
    # 4. Batch Neo4j operations
    # 5. Parallel processing где safe
```

### Caching Strategy
```python
class GraphCoordinatorAgent:
    def __init__(self, ...):
        # ...
        self._entity_cache = {}  # In-memory cache для recent entities
        self._embedding_cache = {}  # Cache embeddings within session
```

## INTEGRATION С CrewAI

```python
def create_agent(self) -> Agent:
    return Agent(
        role="Knowledge Graph Manager", 
        goal="Store entities and relationships in graph database with deduplication",
        backstory=(
            "Expert in graph database operations and entity resolution. "
            "Specializes in maintaining data consistency and avoiding duplicates "
            "while building comprehensive knowledge graphs."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
        max_iter=1,
        memory=False
    )

def create_storage_task(
    self, 
    entities: List[Entity], 
    relationships: List[Relationship],
    chunk_metadata: Dict[str, Any]
) -> Task:
    return Task(
        description=f"Store {len(entities)} entities and {len(relationships)} relationships with deduplication",
        agent=self.create_agent(),
        expected_output="Processing statistics with entities created/merged counts"
    )
```

## ТЕСТЫ

### Test File: `tests/test_agents/test_graph_coordinator.py`

```python
class TestGraphCoordinatorAgent:
    def test_store_knowledge_success(self):
        # Test successful storage of entities + relationships
        
    def test_entity_deduplication(self):
        # Test vector similarity deduplication
        
    def test_llm_merge_confirmation(self):
        # Test LLM-based merge decisions
        
    def test_neo4j_operations(self):
        # Test Neo4j CRUD operations
        
    def test_postgresql_operations(self):
        # Test PostgreSQL vector storage
        
    def test_transaction_rollback(self):
        # Test transaction rollback on errors
        
    def test_batch_processing(self):
        # Test batch operations efficiency
        
    def test_frida_embeddings(self):
        # Test FRIDA embedding generation
        
    def test_similarity_computation(self):
        # Test cosine similarity calculations
        
    def test_performance_large_dataset(self):
        # Test with large entity sets
```

## ERROR HANDLING

### Database Connection Issues
```python
def _handle_database_errors(self, operation: str, error: Exception):
    """Centralized database error handling"""
    
    # 1. Log error с context
    # 2. Attempt reconnection если connection error
    # 3. Rollback transactions
    # 4. Return graceful degradation
```

### Embedding Generation Failures
```python
def _handle_embedding_errors(self, texts: List[str], error: Exception):
    """Handle FRIDA API failures"""
    
    # 1. Fallback к text-based similarity
    # 2. Skip deduplication если embeddings unavailable
    # 3. Log warning но continue processing
```

## SUCCESS CRITERIA

- [ ] CrewAI Agent integration working
- [ ] Neo4j entities и relationships storage
- [ ] PostgreSQL chunks и embeddings storage 
- [ ] Entity deduplication с vector similarity
- [ ] LLM merge confirmation working
- [ ] Transaction management с rollback
- [ ] Batch processing optimized
- [ ] FRIDA embeddings integration
- [ ] Processing statistics accurate
- [ ] All tests pass с 80%+ coverage
- [ ] Performance: < 10s per chunk processing
- [ ] Memory usage: < 500MB per agent

## VALIDATION COMMANDS

```bash
# Unit tests
python -m pytest tests/test_agents/test_graph_coordinator.py -v

# Integration test
python -c "
from src.agents.entity_extractor import EntityExtractorAgent
from src.agents.relationship_analyzer import RelationshipAnalyzerAgent  
from src.agents.graph_coordinator import GraphCoordinatorAgent
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient

# Full pipeline test
extractor = EntityExtractorAgent()
analyzer = RelationshipAnalyzerAgent()
coordinator = GraphCoordinatorAgent(
    Neo4jClient('bolt://neo4j:7687', 'neo4j', 'neo4j'),
    PostgresClient('postgres', 5432, 'worldbuilding', 'postgres', 'postgres')
)

text = 'Гарри Поттер учился в Хогвартсе в Англии.'
chunk_metadata = {'chunk_id': 'test', 'file_name': 'test.md', 'text': text}

entities = extractor.extract_entities(text, chunk_metadata)
relationships = analyzer.analyze_relationships(entities, text)
stats = coordinator.store_knowledge(entities, relationships, chunk_metadata)

print(f'Stored: {stats}')
"
```
# Task 11: Graph Coordinator Agent

## ЦЕЛЬ
Создать CrewAI агент для управления графом знаний (Neo4j) и векторной базой данных (PostgreSQL), включая дедупликацию сущностей и сохранение результатов обработки.

## ФАЙЛ
`src/agents/graph_coordinator.py`

## ОСНОВНЫЕ ТРЕБОВАНИЯ

### 1. CrewAI Agent Integration
- Role: "Knowledge Graph Manager"
- Goal: "Store entities and relationships in graph database with deduplication"
- Backstory: "Expert in graph database operations and entity resolution"

### 2. Dual Database Management
- **Neo4j**: сущности (nodes) + отношения (edges)
- **PostgreSQL**: текстовые чанки + векторные эмбеддинги
- **sentence-transformers** для семантического поиска
- Transactional operations с rollback capability

### 3. Entity Deduplication
- **Vector similarity**: sentence-transformers embeddings
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2` (поддержка русского)
- **Similarity threshold**: 0.85 (настраиваемый)
- **LLM confirmation**: для borderline cases (0.80-0.90)
- **Merge strategy**: combine descriptions, preserve all sources

### 4. Statistics & Monitoring
- Entities created/updated/merged
- Relationships created
- Processing time metrics
- Database operation counts

## АЛГОРИТМ РЕАЛИЗАЦИИ

### Шаг 1: Agent Class Structure
```python
from crewai import Agent, Task
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient
from src.utils.logging_utils import get_agent_logger, log_database_operation

class GraphCoordinatorAgent:
    def __init__(
        self, 
        neo4j_client: Neo4jClient,
        postgres_client: PostgresClient,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        similarity_threshold: float = 0.85
    ):
        self.neo4j = neo4j_client
        self.postgres = postgres_client
        self.embedding_model_name = embedding_model
        self.similarity_threshold = similarity_threshold
        self.logger = get_agent_logger()
        self._embedding_model = None  # Lazy initialization
        
    def create_agent(self) -> Agent:
        # CrewAI Agent creation
        
    def store_knowledge(
        self, 
        entities: List[Entity], 
        relationships: List[Relationship],
        chunk_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Main orchestration method
        
    def store_knowledge_batch(
        self,
        entities_batches: List[List[Entity]],
        relationships_batches: List[List[Relationship]], 
        chunks_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # Batch processing multiple chunks
```

### Шаг 2: Entity Deduplication Core
```python
def deduplicate_entities(self, new_entities: List[Entity]) -> Tuple[List[Entity], Dict[str, Any]]:
    """
    Deduplicate entities using vector similarity + LLM confirmation
    Returns: (deduplicated_entities, merge_statistics)
    """
    
    # Algorithm:
    # 1. Generate embeddings для new entities
    # 2. Найти existing entities того же типа из PostgreSQL  
    # 3. Compute similarity matrix
    # 4. Identify candidates (similarity > threshold)
    # 5. LLM confirmation для borderline cases
    # 6. Merge duplicate entities
    # 7. Return deduplicated list + stats

def _generate_embeddings(self, entities: List[Entity]) -> Dict[str, np.ndarray]:
    """Generate sentence-transformers embeddings for entity names + descriptions"""
    
    # 1. Initialize model если еще не загружен
    if self._embedding_model is None:
        from sentence_transformers import SentenceTransformer
        self._embedding_model = SentenceTransformer(self.embedding_model_name)
    
    # 2. Prepare text для каждой entity (name + description)
    texts = []
    entity_keys = []
    for entity in entities:
        text = entity.name
        if entity.description:
            text += f" - {entity.description}"
        texts.append(text)
        entity_keys.append(entity.name)
    
    # 3. Generate embeddings batch
    embeddings = self._embedding_model.encode(texts, convert_to_numpy=True)
    
    # 4. Return dictionary {entity.name: embedding_vector}
    return dict(zip(entity_keys, embeddings))

def _find_similar_entities(
    self, 
    new_entity: Entity, 
    existing_entities: List[Dict]
) -> List[Tuple[Dict, float]]:
    """Find existing entities similar to new entity"""
    
    # 1. Filter existing entities по типу
    # 2. Compute cosine similarity с new entity embedding
    # 3. Return candidates выше similarity threshold
    # 4. Sort по similarity score

def _confirm_merge_with_llm(
    self, 
    entity1: Entity, 
    entity2_data: Dict, 
    similarity_score: float
) -> bool:
    """Use LLM to confirm if entities should be merged"""
    
    # 1. Build prompt для LLM comparison
    # 2. Call Saiga model
    # 3. Parse yes/no response
    # 4. Return merge decision
```

### Шаг 3: Neo4j Graph Operations
```python
# Cypher queries constants
CREATE_ENTITY_QUERY = """
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

CREATE_RELATIONSHIP_QUERY = """
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

def _store_entities_neo4j(self, entities: List[Entity]) -> Dict[str, int]:
    """Store entities in Neo4j with merge logic"""
    
    # 1. Batch создание entities через транзакцию
    # 2. Handle duplicates через ON MATCH logic
    # 3. Track создание vs updates
    # 4. Return statistics

def _store_relationships_neo4j(self, relationships: List[Relationship]) -> Dict[str, int]:
    """Store relationships in Neo4j"""
    
    # 1. Проверить что source/target entities существуют
    # 2. Создать relationships через MERGE
    # 3. Handle confidence updates
    # 4. Return statistics
```

### Шаг 4: PostgreSQL Vector Operations
```python
def _store_chunk_postgresql(self, chunk_metadata: Dict[str, Any]) -> bool:
    """Store text chunk with embeddings in PostgreSQL"""
    
    # 1. Generate embedding для chunk text
    # 2. Insert в chunks table
    # 3. Handle conflicts (ON CONFLICT DO UPDATE)
    # 4. Return success status

def _store_entities_cache_postgresql(self, entities: List[Entity]) -> bool:
    """Store entities with embeddings for deduplication"""
    
    # 1. Generate embeddings для entity names
    # 2. Insert в entities_cache table
    # 3. Update existing entities если нужно
    # 4. Return success status

def _get_existing_entities_by_type(self, entity_type: str) -> List[Dict]:
    """Retrieve existing entities from PostgreSQL for deduplication"""
    
    # SQL query to get entities с embeddings
    query = """
    SELECT name, type, description, embedding, source_file
    FROM entities_cache 
    WHERE type = %s
    ORDER BY created_at DESC
    """
```

### Шаг 5: Sentence-Transformers Integration
```python
def _get_embedding_model(self):
    """Lazy load sentence-transformers model"""
    if self._embedding_model is None:
        from sentence_transformers import SentenceTransformer
        self._embedding_model = SentenceTransformer(self.embedding_model_name)
    return self._embedding_model

def _generate_text_embedding(self, text: str) -> np.ndarray:
    """Generate embedding for single text"""
    model = self._get_embedding_model()
    return model.encode(text, convert_to_numpy=True)

def _generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
    """Generate embeddings for multiple texts efficiently"""
    model = self._get_embedding_model()
    return model.encode(texts, convert_to_numpy=True)

def _compute_similarity_matrix(
    self, 
    new_embeddings: List[np.ndarray], 
    existing_embeddings: List[np.ndarray]
) -> np.ndarray:
    """Compute cosine similarity matrix between embeddings"""
    
    # 1. Convert to numpy arrays
    new_emb = np.array(new_embeddings)
    existing_emb = np.array(existing_embeddings)
    
    # 2. Normalize vectors
    new_emb_norm = new_emb / np.linalg.norm(new_emb, axis=1, keepdims=True)
    existing_emb_norm = existing_emb / np.linalg.norm(existing_emb, axis=1, keepdims=True)
    
    # 3. Compute cosine similarity
    return np.dot(new_emb_norm, existing_emb_norm.T)
```

## LLM MERGE CONFIRMATION

### Prompt Template для Saiga
```python
MERGE_CONFIRMATION_PROMPT = """### Задача: Определить, являются ли две сущности одинаковыми.

### Сущность 1:
Название: {entity1_name}
Тип: {entity1_type}
Описание: {entity1_description}
Источник: {entity1_source}

### Сущность 2:
Название: {entity2_name} 
Тип: {entity2_type}
Описание: {entity2_description}
Источник: {entity2_source}

### Векторное сходство: {similarity_score:.3f}

### Инструкции:
1. Сравните названия сущностей
2. Учтите контекст и описания
3. Определите, это одна и та же сущность или разные
4. Учтите возможные вариации написания

### Формат ответа (только JSON):
{{
  "should_merge": true/false,
  "reason": "краткое_объяснение_решения"
}}

### Ответ:"""
```

## TRANSACTION MANAGEMENT

```python
def store_knowledge(self, entities, relationships, chunk_metadata):
    """Main method with full transaction support"""
    
    start_time = time.time()
    stats = {
        "entities_processed": 0,
        "entities_created": 0,
        "entities_merged": 0,
        "relationships_created": 0,
        "chunks_stored": 0,
        "processing_time": 0,
        "errors": []
    }
    
    try:
        # 1. Begin transactions в обеих БД
        
        # 2. Store chunk в PostgreSQL first
        self._store_chunk_postgresql(chunk_metadata)
        stats["chunks_stored"] = 1
        
        # 3. Deduplicate entities
        dedupe_entities, dedupe_stats = self.deduplicate_entities(entities)
        stats.update(dedupe_stats)
        
        # 4. Store entities в Neo4j
        entity_stats = self._store_entities_neo4j(dedupe_entities)
        stats.update(entity_stats)
        
        # 5. Store entities cache в PostgreSQL
        self._store_entities_cache_postgresql(dedupe_entities)
        
        # 6. Store relationships в Neo4j
        rel_stats = self._store_relationships_neo4j(relationships)
        stats.update(rel_stats)
        
        # 7. Commit transactions
        
        stats["processing_time"] = time.time() - start_time
        self._log_processing_stats(stats)
        
        return stats
        
    except Exception as e:
        # Rollback both databases
        self.logger.error(f"Failed to store knowledge: {e}")
        stats["errors"].append(str(e))
        # Rollback logic
        raise
```

## PERFORMANCE OPTIMIZATION

### Batch Operations
```python
def store_knowledge_batch(self, entities_batches, relationships_batches, chunks_metadata):
    """Optimized batch processing"""
    
    # 1. Process все chunks в single transaction где возможно
    # 2. Batch entity deduplication
    # 3. Bulk inserts в PostgreSQL
    # 4. Batch Neo4j operations
    # 5. Parallel processing где safe
```

### Caching Strategy
```python
class GraphCoordinatorAgent:
    def __init__(self, ...):
        # ...
        self._entity_cache = {}  # In-memory cache для recent entities
        self._embedding_cache = {}  # Cache embeddings within session
```

## INTEGRATION С CrewAI

```python
def create_agent(self) -> Agent:
    return Agent(
        role="Knowledge Graph Manager", 
        goal="Store entities and relationships in graph database with deduplication",
        backstory=(
            "Expert in graph database operations and entity resolution. "
            "Specializes in maintaining data consistency and avoiding duplicates "
            "while building comprehensive knowledge graphs."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
        max_iter=1,
        memory=False
    )

def create_storage_task(
    self, 
    entities: List[Entity], 
    relationships: List[Relationship],
    chunk_metadata: Dict[str, Any]
) -> Task:
    return Task(
        description=f"Store {len(entities)} entities and {len(relationships)} relationships with deduplication",
        agent=self.create_agent(),
        expected_output="Processing statistics with entities created/merged counts"
    )
```

## ТЕСТЫ

### Test File: `tests/test_agents/test_graph_coordinator.py`

```python
class TestGraphCoordinatorAgent:
    def test_store_knowledge_success(self):
        # Test successful storage of entities + relationships
        
    def test_entity_deduplication(self):
        # Test vector similarity deduplication
        
    def test_llm_merge_confirmation(self):
        # Test LLM-based merge decisions
        
    def test_neo4j_operations(self):
        # Test Neo4j CRUD operations
        
    def test_postgresql_operations(self):
        # Test PostgreSQL vector storage
        
    def test_transaction_rollback(self):
        # Test transaction rollback on errors
        
    def test_batch_processing(self):
        # Test batch operations efficiency
        
    def test_frida_embeddings(self):
        # Test FRIDA embedding generation
        
    def test_similarity_computation(self):
        # Test cosine similarity calculations
        
    def test_performance_large_dataset(self):
        # Test with large entity sets
```

## ERROR HANDLING

### Database Connection Issues
```python
def _handle_database_errors(self, operation: str, error: Exception):
    """Centralized database error handling"""
    
    # 1. Log error с context
    # 2. Attempt reconnection если connection error
    # 3. Rollback transactions
    # 4. Return graceful degradation
```

### Embedding Generation Failures
```python
def _handle_embedding_errors(self, texts: List[str], error: Exception):
    """Handle sentence-transformers failures"""
    
    # 1. Log error с context
    # 2. Fallback к text-based similarity (Levenshtein distance)
    # 3. Skip deduplication если embeddings unavailable
    # 4. Continue processing с warning
    # 5. Reload model если model corruption detected
```

## SUCCESS CRITERIA

- [ ] CrewAI Agent integration working
- [ ] Neo4j entities и relationships storage
- [ ] PostgreSQL chunks и embeddings storage 
- [ ] Entity deduplication с vector similarity
- [ ] LLM merge confirmation working
- [ ] Transaction management с rollback
- [ ] Batch processing optimized
- [ ] FRIDA embeddings integration
- [ ] Processing statistics accurate
- [ ] All tests pass с 80%+ coverage
- [ ] Performance: < 10s per chunk processing
- [ ] Memory usage: < 500MB per agent

## VALIDATION COMMANDS

```bash
# Unit tests
python -m pytest tests/test_agents/test_graph_coordinator.py -v

# Integration test
python -c "
from src.agents.entity_extractor import EntityExtractorAgent
from src.agents.relationship_analyzer import RelationshipAnalyzerAgent  
from src.agents.graph_coordinator import GraphCoordinatorAgent
from src.database.neo4j_client import Neo4jClient
from src.database.postgres_client import PostgresClient

# Full pipeline test
extractor = EntityExtractorAgent()
analyzer = RelationshipAnalyzerAgent()
coordinator = GraphCoordinatorAgent(
    Neo4jClient('bolt://neo4j:7687', 'neo4j', 'neo4j'),
    PostgresClient('postgres', 5432, 'worldbuilding', 'postgres', 'postgres')
)

text = 'Гарри Поттер учился в Хогвартсе в Англии.'
chunk_metadata = {'chunk_id': 'test', 'file_name': 'test.md', 'text': text}

entities = extractor.extract_entities(text, chunk_metadata)
relationships = analyzer.analyze_relationships(entities, text)
stats = coordinator.store_knowledge(entities, relationships, chunk_metadata)

print(f'Stored: {stats}')
"
```
