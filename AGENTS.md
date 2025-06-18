# AGENTS.md - Implementation Instructions for ChatGPT Codex

## CONTEXT
You are implementing a CrewAI multi-agent system for extracting entities and relationships from markdown files, then storing them in Neo4j graph database and PostgreSQL vector database.

## TECH STACK
- **Framework**: CrewAI 0.28.8
- **Models**: Ollama (NuExtract, Saiga), FRIDA embeddings
- **Databases**: Neo4j Community 5.x, PostgreSQL 15 + pgvector
- **Languages**: Python 3.11, strictly typed with Pydantic models

## IMPLEMENTATION REQUIREMENTS

### 1. Create Entity Extractor Agent
**File**: `src/agents/entity_extractor.py`

**TASK**: Implement a CrewAI agent that uses NuExtract model via Ollama to extract named entities from text chunks.

**SPECIFICATIONS**:
```python
from crewai import Agent, Task
from pydantic import BaseModel
from typing import List, Optional
import json
import requests
import tiktoken

class Entity(BaseModel):
    name: str
    type: str  # person, location, organization, concept, object
    description: Optional[str] = None
    mentions: List[str] = []
    confidence: float
    source_chunk: str
    context: str

class EntityExtractorAgent:
    def __init__(self, ollama_base_url: str = "http://ollama:11434"):
        self.ollama_url = ollama_base_url
        self.model_name = "nuextract"
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Named Entity Recognition Specialist",
            goal="Extract entities from text chunks with high accuracy",
            backstory="Expert in identifying persons, locations, organizations, concepts, and objects in narrative texts",
            verbose=True,
            allow_delegation=False
        )
    
    def extract_entities(self, chunk_text: str, chunk_metadata: dict, entity_types: List[str]) -> List[Entity]:
        """Extract entities from text chunk using NuExtract model"""
        # IMPLEMENT: Call Ollama API with direct HTTP requests
        # IMPLEMENT: Parse JSON response 
        # IMPLEMENT: Validate entities against confidence threshold (0.7)
        # IMPLEMENT: Error handling with 3 retries
        pass
    
    def _call_ollama(self, prompt: str) -> dict:
        """Direct HTTP call to Ollama API"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
        return response.json()
```

**PROMPT TEMPLATE** (use exactly this format):
```python
def get_extraction_prompt(text_chunk: str, entity_types: List[str]) -> str:
    return f"""### Task: Extract entities from the text chunk below.

### Entity Types to Extract:
{', '.join(entity_types)}

### Text Chunk:
{text_chunk}

### Output Format (valid JSON only):
{{
  "entities": [
    {{
      "name": "entity_name",
      "type": "entity_type", 
      "description": "brief_description",
      "mentions": ["mention1", "mention2"],
      "confidence": 0.95,
      "context": "surrounding_text_50_chars"
    }}
  ]
}}

### Rules:
1. Extract only entities that clearly belong to specified types
2. Confidence score 0.7-1.0 based on context clarity
3. Include all text variations in mentions array
4. Keep descriptions under 100 characters
5. Focus on narrative-relevant entities only
6. Return valid JSON only, no explanations

### Response:"""
```

**REQUIRED TESTS**: `tests/test_agents/test_entity_extractor.py`
```python
def test_extract_entities_success():
    # Test successful entity extraction
    pass

def test_extract_entities_empty_input():
    # Test with empty text
    pass

def test_extract_entities_low_confidence():
    # Test filtering low confidence entities
    pass

def test_ollama_connection_failure():
    # Test retry logic on connection failure
    pass
```

### 2. Create Relationship Analyzer Agent
**File**: `src/agents/relationship_analyzer.py`

**TASK**: Implement agent that analyzes relationships between extracted entities using Saiga model.

**SPECIFICATIONS**:
```python
class Relationship:
    source_entity: str
    target_entity: str
    relation_type: str  # knows, located_in, part_of, owns, related_to, interacts_with
    description: str
    confidence: float
    source_text: str

class RelationshipAnalyzerAgent:
    def __init__(self, ollama_base_url: str = "http://ollama:11434"):
        self.ollama_url = ollama_base_url.rstrip("/")
        self.model_name = "ilyagusev/saiga_llama3"
        self.logger = get_agent_logger()
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_pairs_per_chunk = 10
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Relationship Analysis Expert",
            goal="Identify relationships between entities in text",
            backstory=(
                "Specialist in understanding connections and relationships between narrative elements. "
                "Expert in Russian language analysis and context interpretation."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[],
            max_iter=1,
            memory=False
        )
    
    def analyze_relationships(
        self, 
        entities: List[Entity], 
        original_text: str,
        confidence_threshold: float = 0.75
    ) -> List[Relationship]:
        """Analyze relationships between entities in the given text"""
        # Generate and prioritize entity pairs
        pairs = self._generate_entity_pairs(entities)
        prioritized_pairs = self._prioritize_entity_pairs(pairs, original_text)
        
        relationships = []
        for entity1, entity2 in prioritized_pairs:
            relationship = self._analyze_entity_pair(
                entity1, entity2, original_text, confidence_threshold
            )
            if relationship:
                relationships.append(relationship)
                log_relationship_analysis(relationship)
                
        return relationships
        
    def analyze_relationships_batch(
        self,
        entities_per_chunk: List[List[Entity]],
        original_texts: List[str],
        confidence_threshold: float = 0.75
    ) -> List[List[Relationship]]:
        """Batch processing of multiple chunks"""
        results = []
        total_chunks = len(entities_per_chunk)
        
        for i, (entities, text) in enumerate(zip(entities_per_chunk, original_texts)):
            self.logger.info(f"Processing chunk {i+1}/{total_chunks}")
            try:
                chunk_relationships = self.analyze_relationships(
                    entities, text, confidence_threshold
                )
                results.append(chunk_relationships)
            except Exception as e:
                self.logger.error(f"Error processing chunk {i+1}: {str(e)}")
                results.append([])
                
        return results
```

**PROMPT TEMPLATE**:
```python
RELATIONSHIP_PROMPT_TEMPLATE = """### Задача: Определить отношения между сущностями в тексте.

### Сущности для анализа:
- Сущность 1: {entity1_name} (тип: {entity1_type})
- Сущность 2: {entity2_name} (тип: {entity2_type})

### Контекст (оригинальный текст):
{text}

### Возможные типы отношений:
- knows (знает/знаком с)
- located_in (находится в/расположен в)
- part_of (является частью/принадлежит)
- owns (владеет/обладает)
- related_to (связан с/относится к)
- interacts_with (взаимодействует с/работает с)

### Инструкции:
1. Найдите упоминания обеих сущностей в тексте
2. Определите есть ли между ними отношение
3. Выберите наиболее подходящий тип отношения
4. Оцените уверенность от 0.75 до 1.0
5. Укажите фрагмент текста, подтверждающий отношение

### Формат ответа (только JSON, без объяснений):
{{
  "relationship": {{
    "source_entity": "{entity1_name}",
    "target_entity": "{entity2_name}",
    "relation_type": "тип_отношения",
    "description": "краткое_описание_отношения",
    "confidence": 0.85,
    "source_text": "фрагмент_текста_подтверждающий_отношение"
  }}
}}

### Если отношения нет:
{{
  "relationship": null
}}

### Ответ:"""
```

**KEY FEATURES**:
1. Entity Pair Generation
   - Optimized pair generation with max 10 pairs per chunk
   - Filters same-type pairs (except person-person)
   - Prioritizes pairs by proximity in text

2. Relationship Analysis
   - Uses Saiga model via Ollama API
   - Retry logic with exponential backoff
   - Confidence threshold filtering (0.75)
   - Robust JSON parsing with error handling

3. Batch Processing
   - Efficient processing of multiple chunks
   - Progress tracking and error handling
   - Maintains chunk-level relationship grouping

4. Performance Optimizations
   - Pair prioritization by text proximity
   - Type-based pair filtering
   - Batch processing for multiple chunks
   - Efficient error handling and logging

**REQUIRED TESTS**: `tests/test_agents/test_relationship_analyzer.py`
```python
def test_analyze_relationships_success():
    # Test successful relationship detection
    
def test_analyze_relationships_no_relation():
    # Test case where no relationship exists
    
def test_entity_pair_generation():
    # Test pair generation and optimization
    
def test_confidence_filtering():
    # Test filtering low confidence relationships
    
def test_batch_processing():
    # Test batch processing efficiency
    
def test_saiga_response_parsing():
    # Test parsing various Saiga response formats
    
def test_russian_text_analysis():
    # Test with Russian language text
    
def test_pair_prioritization():
    # Test proximity-based pair prioritization
    
def test_large_entity_set():
    # Test performance with many entities (>10)
```

### 3. Create Graph Coordinator Agent
**File**: `src/agents/graph_coordinator.py`

**TASK**: Implement agent that manages Neo4j graph and PostgreSQL vector storage with entity deduplication.

**SPECIFICATIONS**:
```python
class GraphCoordinator:
    def __init__(self, neo4j_client, postgres_client, embedding_model):
        self.neo4j = neo4j_client
        self.postgres = postgres_client
        self.embedder = embedding_model
        self.similarity_threshold = 0.85
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Knowledge Graph Manager",
            goal="Store entities and relationships in graph database with deduplication",
            backstory="Expert in graph database operations and entity resolution",
            verbose=True,
            allow_delegation=False
        )
    
    def store_knowledge(self, entities: List[Entity], relationships: List[Relationship], chunk_metadata: dict) -> dict:
        """Store entities and relationships in databases with deduplication"""
        # IMPLEMENT: Entity deduplication using vector similarity
        # IMPLEMENT: Store unique entities in Neo4j
        # IMPLEMENT: Store relationships in Neo4j
        # IMPLEMENT: Store chunk text with embeddings in PostgreSQL
        # IMPLEMENT: Return processing statistics
        pass
    
    def deduplicate_entities(self, new_entities: List[Entity]) -> List[Entity]:
        """Deduplicate entities using vector similarity and LLM confirmation"""
        # IMPLEMENT: Generate embeddings for entity names
        # IMPLEMENT: Compare with existing entities in PostgreSQL
        # IMPLEMENT: LLM-based confirmation for similarity > threshold
        # IMPLEMENT: Merge duplicate entities
        pass
```

**CYPHER QUERIES** (include these exact queries):
```python
CREATE_ENTITY_QUERY = """
MERGE (e:Entity {name: $name, type: $type})
ON CREATE SET e.description = $description, e.created_at = datetime()
ON MATCH SET e.description = $description, e.updated_at = datetime()
RETURN e
"""

CREATE_RELATIONSHIP_QUERY = """
MATCH (a:Entity {name: $source_entity})
MATCH (b:Entity {name: $target_entity})
MERGE (a)-[r:RELATED {type: $relation_type}]->(b)
ON CREATE SET r.description = $description, r.confidence = $confidence
RETURN r
"""

FIND_SIMILAR_ENTITIES_QUERY = """
MATCH (e:Entity)
WHERE e.type = $entity_type
RETURN e.name as name, e.description as description
"""
```

**REQUIRED TESTS**: `tests/test_agents/test_graph_coordinator.py`

### 4. Create CrewAI Workflow
**File**: `src/agents/crew.py`

**TASK**: Orchestrate all agents in sequential workflow.

**SPECIFICATIONS**:
```python
from crewai import Crew, Process
from .entity_extractor import EntityExtractorAgent
from .relationship_analyzer import RelationshipAnalyzerAgent
from .graph_coordinator import GraphCoordinator

class WorldbuildingCrew:
    def __init__(self, config: dict):
        self.entity_extractor = EntityExtractorAgent(config['ollama_url'])
        self.relationship_analyzer = RelationshipAnalyzerAgent(config['ollama_url'])
        self.graph_coordinator = GraphCoordinator(
            config['neo4j_client'],
            config['postgres_client'],
            config['embedding_model']
        )
        
    def create_crew(self) -> Crew:
        """Create and configure the agent crew"""
        # IMPLEMENT: Create agents
        # IMPLEMENT: Define tasks
        # IMPLEMENT: Set up sequential process
        # IMPLEMENT: Configure error handling
        pass
    
    def process_chunk(self, chunk_text: str, chunk_metadata: dict) -> dict:
        """Process a single text chunk through the full pipeline"""
        # IMPLEMENT: Execute crew workflow
        # IMPLEMENT: Return processing results
        pass

def create_tasks(agents: dict, chunk_data: dict) -> List[Task]:
    """Create tasks for the crew"""
    return [
        Task(
            description="Extract entities from text chunk",
            agent=agents['entity_extractor'],
            expected_output="List of Entity objects in JSON format"
        ),
        Task(
            description="Analyze relationships between extracted entities",
            agent=agents['relationship_analyzer'],
            expected_output="List of Relationship objects in JSON format"
        ),
        Task(
            description="Store entities and relationships in databases",
            agent=agents['graph_coordinator'],
            expected_output="Processing statistics dictionary"
        )
    ]
```

**REQUIRED TESTS**: `tests/test_agents/test_crew.py`

## IMPLEMENTATION NOTES

### Error Handling Requirements
- All Ollama API calls must have 3-retry logic with exponential backoff
- Database operations must be wrapped in transactions
- Invalid JSON responses must be logged and skipped
- Network timeouts: 30 seconds for Ollama, 10 seconds for databases

### Performance Requirements
- Process chunks concurrently (max 3 parallel)
- Entity deduplication must use batch operations
- Database connections must use connection pooling
- Memory usage must not exceed 1GB per agent

### Logging Requirements
```python
import logging
logger = logging.getLogger(__name__)

# Use these exact log formats:
logger.info(f"Processing chunk {chunk_id}: {len(entities)} entities extracted")
logger.warning(f"Low confidence entity filtered: {entity_name} ({confidence})")
logger.error(f"Failed to extract entities from chunk {chunk_id}: {error}")
```

### Configuration Schema
```python
# src/config/agent_config.py
class AgentConfig(BaseModel):
    ollama_url: str = "http://ollama:11434"
    entity_types: List[str] = ["person", "location", "organization", "concept", "object"]
    confidence_threshold: float = 0.7
    similarity_threshold: float = 0.85
    max_retries: int = 3
    batch_size: int = 10
    chunk_size: int = 500
    chunk_overlap: int = 100
```

### Chunking Implementation (without LangChain)
```python
# src/utils/chunking.py
import tiktoken
from typing import List, Dict

def recursive_chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    separators: List[str] = ["\n\n", "\n", ".", " "]
) -> List[Dict]:
    """
    Recursive text chunking implementation (replaces LangChain)
    """
    tokenizer = tiktoken.get_encoding("cl100k_base")
    chunks = []
    
    def _split_text(text: str, separators: List[str]) -> List[str]:
        # IMPLEMENT: Recursive splitting logic
        # IMPLEMENT: Token counting
        # IMPLEMENT: Overlap handling
        pass
    
    return chunks
```

### Direct Ollama API Calls
```python
# src/utils/ollama_client.py
import requests
import json
from typing import Dict, Any

class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
    
    def generate(self, model: str, prompt: str, format: str = "json") -> Dict[Any, Any]:
        """Direct HTTP call to Ollama API (replaces LangChain wrapper)"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": format
        }
        
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()
```

## VALIDATION COMMANDS
```bash
# Test individual agents
python -m pytest tests/test_agents/test_entity_extractor.py -v
python -m pytest tests/test_agents/test_relationship_analyzer.py -v
python -m pytest tests/test_agents/test_graph_coordinator.py -v

# Test full crew
python -m pytest tests/test_agents/test_crew.py -v

# Test with sample data
python src/agents/crew.py --test-mode --input-file data/sample_md/test.md
```

## SUCCESS CRITERIA
- [ ] All agents pass unit tests with 80%+ coverage
- [ ] Entity extraction accuracy >85% on test data
- [ ] Relationship detection accuracy >75% on test data  
- [ ] Deduplication reduces duplicates by >90%
- [ ] Processing time <2 minutes per 1MB markdown file
- [ ] No memory leaks during batch processing
- [ ] All database operations are transactional
- [ ] Error recovery works for all failure scenarios

## IMPLEMENTATION ORDER
1. Create data models (Entity, Relationship) first
2. Implement EntityExtractorAgent with tests
3. Implement RelationshipAnalyzerAgent with tests
4. Implement GraphCoordinator with tests
5. Create CrewAI workflow integration
6. Add comprehensive error handling
7. Performance optimization and testing
