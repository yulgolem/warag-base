from crewai import Agent, Task
import requests
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from itertools import combinations
from src.models.entities import Entity
from src.models.relationships import Relationship
from src.utils.logging_utils import get_agent_logger, log_relationship_analysis

DEFAULT_RELATION_TYPES = [
    "knows", "located_in", "part_of", "owns", "related_to", "interacts_with"
]

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

    def _generate_entity_pairs(self, entities: List[Entity]) -> List[Tuple[Entity, Entity]]:
        """Generate entity pairs for relationship analysis with optimization"""
        # Create all possible pairs
        all_pairs = list(combinations(entities, 2))
        
        # Filter pairs of same type (except person-person)
        filtered_pairs = [
            pair for pair in all_pairs
            if pair[0].type != pair[1].type or pair[0].type == "person"
        ]
        
        # Limit number of pairs
        return filtered_pairs[:self.max_pairs_per_chunk]

    def _prioritize_entity_pairs(
        self, 
        pairs: List[Tuple[Entity, Entity]], 
        text: str
    ) -> List[Tuple[Entity, Entity]]:
        """Prioritize entity pairs by proximity in text"""
        def get_priority_score(pair: Tuple[Entity, Entity]) -> float:
            entity1, entity2 = pair
            # Find positions of entities in text
            pos1 = text.lower().find(entity1.name.lower())
            pos2 = text.lower().find(entity2.name.lower())
            
            if pos1 == -1 or pos2 == -1:
                return 0.0
                
            # Calculate distance between mentions
            distance = abs(pos1 - pos2)
            
            # Different entity types get higher priority
            type_priority = 2.0 if entity1.type != entity2.type else 1.0
            
            # Calculate final score (lower distance = higher score)
            return type_priority * (1.0 / (distance + 1))
            
        # Sort pairs by priority score
        return sorted(pairs, key=get_priority_score, reverse=True)

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry logic with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)

    def _analyze_entity_pair(
        self, 
        entity1: Entity, 
        entity2: Entity, 
        text: str,
        confidence_threshold: float
    ) -> Optional[Relationship]:
        """Analyze relationship between two entities"""
        # Ограничиваем контекст до 500 символов вокруг упоминаний сущностей
        context = self._get_relevant_context(text, entity1.name, entity2.name)
        
        prompt = RELATIONSHIP_PROMPT_TEMPLATE.format(
            entity1_name=entity1.name,
            entity1_type=entity1.type,
            entity2_name=entity2.name,
            entity2_type=entity2.type,
            text=context
        )

        def call_ollama():
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 256,  # Ограничиваем длину ответа
                        "temperature": 0.1,  # Уменьшаем случайность
                        "top_k": 10,         # Ограничиваем варианты
                        "top_p": 0.1         # Увеличиваем определенность
                    }
                },
                timeout=300  # Увеличиваем таймаут до 5 минут
            )
            response.raise_for_status()
            return response.json()

        try:
            result = self._retry_with_backoff(call_ollama)
            response_text = result.get("response", "")
            
            # Extract JSON from response
            try:
                # Find JSON object in response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start == -1 or json_end == 0:
                    return None
                    
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                if not data.get("relationship"):
                    return None
                    
                rel_data = data["relationship"]
                
                # Validate confidence threshold
                if rel_data.get("confidence", 0) < confidence_threshold:
                    return None
                    
                return Relationship(
                    source_entity=rel_data["source_entity"],
                    target_entity=rel_data["target_entity"],
                    relation_type=rel_data["relation_type"],
                    description=rel_data["description"],
                    confidence=rel_data["confidence"],
                    source_text=rel_data["source_text"]
                )
                
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON from response: {response_text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error analyzing entity pair: {str(e)}")
            return None

    def _get_relevant_context(self, text: str, entity1: str, entity2: str) -> str:
        """Extract relevant context around entity mentions"""
        # Находим позиции упоминаний
        pos1 = text.lower().find(entity1.lower())
        pos2 = text.lower().find(entity2.lower())
        
        if pos1 == -1 or pos2 == -1:
            return text[:500]  # Если не нашли, берем начало текста
            
        # Определяем границы контекста
        start = max(0, min(pos1, pos2) - 250)
        end = min(len(text), max(pos1, pos2) + 250)
        
        return text[start:end]

    def analyze_relationships(
        self, 
        entities: List[Entity], 
        original_text: str,
        confidence_threshold: float = 0.75
    ) -> List[Relationship]:
        """Main function for relationship analysis"""
        if len(entities) < 2:
            return []
            
        start_time = time.time()
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
                
        # Логируем результаты анализа
        processing_time = time.time() - start_time
        log_relationship_analysis(
            entities_count=len(entities),
            relationships_found=len(relationships),
            processing_time=processing_time
        )
                
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