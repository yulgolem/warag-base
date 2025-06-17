# MVP Technical Specification: Worldbuilding Assistant

## Overview
Создание контейнеризованного ассистента для писателя с функциями извлечения сущностей из markdown-файлов, построения графа связей и семантического поиска.

## Tech Stack
- **Backend**: Python 3.11, CrewAI, LangChain
- **Frontend**: Streamlit (доступен на localhost:8501)
- **Databases**: PostgreSQL 15 + pgvector, Neo4j Community 5.x
- **AI**: Ollama (NuExtract, Saiga), FRIDA embeddings
- **Infrastructure**: Docker Compose

## File Structure
```
worldbuilding-assistant/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── Dockerfile
├── src/
│   ├── __init__.py
│   ├── main.py                 # Streamlit app
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── crew.py            # CrewAI setup
│   │   ├── entity_extractor.py
│   │   ├── relationship_analyzer.py
│   │   ├── graph_coordinator.py
│   │   └── chat_agent.py      # RAG-based chat with knowledge graph
│   ├── models/
│   │   ├── __init__.py
│   │   ├── entities.py        # Data models
│   │   └── relationships.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── neo4j_client.py
│   │   └── postgres_client.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── chunking.py
│   │   ├── logging_utils.py
│   │   └── deduplication.py
│   └── ui/
│       ├── __init__.py
│       ├── components.py      # Streamlit components
│       ├── pages.py          # UI pages
│       └── chat_interface.py  # Chat UI component
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_database/
│   ├── test_utils/
│   └── test_integration/
├── data/
│   ├── sample_md/            # Тестовые MD файлы
│   └── outputs/             # Результаты обработки
└── README.md
```

## Development Roadmap

### Phase 1: Infrastructure Setup (Tasks 1-8)

#### Task 1: Create Docker Compose Configuration
**File**: `docker-compose.yml`
**Deliverable**: Полностью рабочий docker-compose файл
**Requirements**:
- PostgreSQL 15 с pgvector extension
- Neo4j Community 5.x (порт 7474 для браузера, 7687 для bolt)
- Ollama с автозагрузкой моделей (nuextract, saiga)
- Streamlit app service (порт 8501 доступен на localhost:8501)
- Healthchecks для всех сервисов
- Именованные volumes для персистентности
- Network configuration
- Зависимости между сервисами (app зависит от всех БД)

**Test**: `tests/test_integration/test_docker_setup.py`
```python
def test_all_services_healthy():
    # Check PostgreSQL connection
    # Check Neo4j connection  
    # Check Ollama models loaded
    # Check Streamlit accessible on localhost:8501
    pass
```

#### Task 2: Environment Configuration
**File**: `.env.example`, `src/config/settings.py`
**Deliverable**: Система конфигурации
**Requirements**:
- Pydantic BaseSettings для типизированной конфигурации
- Секции: DATABASE, NEO4J, OLLAMA, CHUNKING, UI
- Валидация обязательных параметров
- Default values для разработки

**Test**: `tests/test_config/test_settings.py`

#### Task 3: Database Clients Setup
**Files**: `src/database/postgres_client.py`, `src/database/neo4j_client.py`
**Deliverable**: Клиенты для работы с БД
**Requirements**:
- PostgreSQL client с поддержкой pgvector
- Neo4j client с connection pooling
- Error handling и reconnection logic
- Connection health checks

**Test**: `tests/test_database/test_clients.py`

#### Task 4: Data Models Definition
**Files**: `src/models/entities.py`, `src/models/relationships.py`
**Deliverable**: Pydantic модели
**Requirements**:
```python
class Entity(BaseModel):
    id: Optional[str]
    name: str
    type: str
    description: Optional[str]
    source_file: str
    chunk_id: str
    confidence: float
    
class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    relation_type: str
    description: Optional[str]
    confidence: float
```

**Test**: `tests/test_models/test_data_models.py`

#### Task 5: Chunking System
**File**: `src/utils/chunking.py`
**Deliverable**: Система разбиения текста на чанки
**Requirements**:
- RecursiveCharacterTextSplitter из LangChain
- chunk_size=500, chunk_overlap=100 (настраиваемо)
- Поддержка markdown разделителей: ["\n\n", "\n", ".", " "]
- Метаданные для каждого чанка (file_name, chunk_id, tokens_count)

**Test**: `tests/test_utils/test_chunking.py`
```python
def test_chunk_markdown():
    # Test chunk size limits
    # Test overlap preservation  
    # Test metadata generation
    pass
```

#### Task 6: Logging System
**File**: `src/utils/logging_utils.py`
**Deliverable**: Система логирования
**Requirements**:
- Structured logging (JSON для машины, human-readable для UI)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Separate loggers: agents, database, ui
- Thread-safe для CrewAI

**Test**: `tests/test_utils/test_logging.py`

#### Task 7: Basic Streamlit App Structure
**Files**: `src/main.py`, `src/ui/components.py`
**Deliverable**: Базовая структура UI
**Requirements**:
- Sidebar с настройками
- Main area для загрузки файлов
- Expander для human logs
- Expander для JSON debug output
- Session state management

**Test**: `tests/test_ui/test_streamlit_components.py`

#### Task 8: Project Dependencies
**Files**: `requirements.txt`, `Dockerfile`
**Deliverable**: Контейнеризация приложения
**Requirements**:
```
crewai==0.28.8
streamlit==1.29.0
langchain==0.1.5
neo4j==5.15.0
psycopg2-binary==2.9.9
pgvector==0.2.4
pydantic==2.5.0
ollama==0.1.7
pytest==7.4.3
```

**Test**: `tests/test_integration/test_dockerfile.py`

### Phase 2: Agent System (Tasks 9-13)

#### Task 9: Entity Extractor Agent
**File**: `src/agents/entity_extractor.py`
**Deliverable**: CrewAI агент для извлечения сущностей
**Requirements**:
- Использует NuExtract через Ollama
- Настраиваемые типы сущностей: ["person", "location", "organization", "concept", "object"]
- JSON output format
- Error handling для LLM failures
- Batch processing для множественных чанков

**Template**:
```python
class EntityExtractorAgent:
    def __init__(self, ollama_client):
        self.role = "Named Entity Recognition Specialist"
        self.goal = "Extract entities from text chunks"
        self.backstory = "Expert in identifying entities in narrative texts"
        
    def extract_entities(self, chunk: str) -> List[Entity]:
        # NuExtract prompt template
        # JSON parsing and validation
        # Error handling
        pass
```

**Test**: `tests/test_agents/test_entity_extractor.py`

#### Task 10: Relationship Analyzer Agent  
**File**: `src/agents/relationship_analyzer.py`
**Deliverable**: CrewAI агент для анализа связей
**Requirements**:
- Использует Saiga через Ollama
- Входные данные: список сущностей + оригинальный текст
- Определяет связи типа: "knows", "located_in", "part_of", "owns", "related_to"
- Confidence score для каждой связи

**Test**: `tests/test_agents/test_relationship_analyzer.py`

#### Task 11: Graph Coordinator Agent
**File**: `src/agents/graph_coordinator.py`
**Deliverable**: Агент для управления графом и векторной БД
**Requirements**:
- Сохранение entities в Neo4j
- Сохранение chunks в PostgreSQL с векторными эмбеддингами
- Entity deduplication с порогом similarity_threshold=0.85
- Статистика обработки (entities_found, relationships_created, duplicates_merged)

**Test**: `tests/test_agents/test_graph_coordinator.py`

#### Task 12: Chat Agent (RAG)
**File**: `src/agents/chat_agent.py`
**Deliverable**: RAG-агент для ответов на вопросы о мире
**Requirements**:
- Hybrid search: векторный поиск + граф traversal
- Context retrieval из Neo4j и PostgreSQL
- Использует Saiga для генерации ответов
- Memory для контекста беседы
- Citing sources (какие сущности/файлы использованы)

**Template**:
```python
class ChatAgent:
    def __init__(self, neo4j_client, postgres_client, ollama_client):
        self.role = "World Knowledge Assistant"
        self.goal = "Answer questions about worldbuilding entities and relationships"
        
    def answer_question(self, question: str, chat_history: List[dict]) -> str:
        # 1. Extract entities from question
        # 2. Search similar chunks in PostgreSQL 
        # 3. Get related entities from Neo4j graph
        # 4. Combine context and generate answer
        # 5. Include source citations
        pass
```

**Test**: `tests/test_agents/test_chat_agent.py`

#### Task 13: CrewAI Integration
**File**: `src/agents/crew.py`
**Deliverable**: Настройка команды агентов
**Requirements**:
- Sequential task execution: EntityExtractor → RelationshipAnalyzer → GraphCoordinator
- Chat agent работает независимо для вопросов
- Task definitions с четкими inputs/outputs
- Progress tracking
- Error propagation между агентами

**Test**: `tests/test_agents/test_crew_integration.py`

### Phase 3: Core Features (Tasks 14-18)

#### Task 14: Entity Deduplication System
**File**: `src/utils/deduplication.py`
**Deliverable**: LLM-based дедупликация сущностей
**Requirements**:
- Векторное сравнение названий сущностей (FRIDA embeddings)
- LLM confirmation для similarity > threshold
- Merge strategies: combine descriptions, preserve all source references
- Interactive mode поддержка (user confirmation)

**Test**: `tests/test_utils/test_deduplication.py`

#### Task 15: File Processing Pipeline
**File**: `src/utils/file_processor.py`
**Deliverable**: Обработчик MD файлов
**Requirements**:
- Batch upload через Streamlit file_uploader
- Progress bar с real-time updates
- Error handling для individual files
- Resume capability для interrupted processing

**Test**: `tests/test_utils/test_file_processor.py`

#### Task 16: Chat Interface Component
**File**: `src/ui/chat_interface.py`
**Deliverable**: Streamlit компонент для чата
**Requirements**:
- Chat input с историей сообщений
- Real-time ответы от ChatAgent
- Отображение источников (entities/files used)
- Clear chat history функция
- Auto-scroll to new messages

**Test**: `tests/test_ui/test_chat_interface.py`

#### Task 17: Settings Management UI
**File**: `src/ui/pages.py` (Settings page)
**Deliverable**: UI для конфигурации
**Requirements**:
- Interactive mode toggle
- Model selection (NuExtract/Saiga)
- Chunking parameters (size, overlap)
- Entity types configuration
- Database connection status

**Test**: `tests/test_ui/test_settings_page.py`

#### Task 18: Logging Display Components  
**File**: `src/ui/components.py` (Logging components)
**Deliverable**: Real-time логи в UI
**Requirements**:
- Human-readable logs с автообновлением
- JSON debug output с copy-to-clipboard
- Log filtering по уровням
- Session log persistence

**Test**: `tests/test_ui/test_logging_components.py`

### Phase 4: Integration & Testing (Tasks 19-22)

#### Task 19: End-to-End Processing Flow
**File**: `src/main.py` (Main processing logic)
**Deliverable**: Полный цикл обработки файла + чат
**Requirements**:
- File upload → Chunking → Entity extraction → Relationship analysis → Graph storage
- Chat interface интегрированный в основной UI
- Progress tracking на каждом этапе
- Error recovery и rollback
- Results summary display

**Test**: `tests/test_integration/test_e2e_processing.py`

#### Task 20: Database Schema Setup
**Files**: `src/database/migrations/`
**Deliverable**: Инициализация схем БД
**Requirements**:
- PostgreSQL: chunks table с vector column
- Neo4j: constraints и indexes для entities/relationships
- Initial data setup scripts
- Health check queries

**Test**: `tests/test_database/test_schema.py`

#### Task 21: Sample Data & Documentation
**Files**: `data/sample_md/`, `README.md`
**Deliverable**: Тестовые данные и документация
**Requirements**:
- 5-10 markdown файлов с разным содержанием
- Setup instructions
- API documentation для агентов
- Chat examples и use cases
- Troubleshooting guide

**Test**: `tests/test_integration/test_sample_data.py`

#### Task 22: Comprehensive Test Suite
**Files**: Complete test coverage
**Deliverable**: 80%+ test coverage
**Requirements**:
- Unit tests для всех модулей
- Integration tests для agent workflows
- UI tests для Streamlit components (включая чат)
- Performance tests для batch processing
- Error scenario testing

**Test Coverage Report**: pytest-cov с HTML отчетом

## Acceptance Criteria

### Functional Requirements
1. ✅ Docker Compose поднимает все сервисы без ошибок (в пределах 32GB RAM)
2. ✅ Загрузка MD файлов через Streamlit UI работает
3. ✅ Извлечение сущностей из текста с NuExtract
4. ✅ Анализ связей между сущностями с Saiga  
5. ✅ Сохранение в Neo4j граф и PostgreSQL векторы
6. ✅ Дедупликация сущностей работает корректно
7. ✅ **Chat с WorldBuildingAgent для вопросов о сущностях**
8. ✅ **RAG поиск с цитированием источников**
9. ✅ Real-time логи отображаются в UI
10. ✅ Настройки сохраняются и применяются
11. ✅ JSON debug output доступен для копирования
12. ✅ Обработка множественных файлов с progress tracking

### Technical Requirements
1. ✅ Test coverage ≥ 80%
2. ✅ All services have health checks
3. ✅ Graceful error handling на всех уровнях
4. ✅ Thread-safe operations для concurrent processing
5. ✅ Configurable через environment variables
6. ✅ Structured logging в JSON формате
7. ✅ Type hints для всех функций
8. ✅ Docstrings для всех public methods
9. ✅ No hardcoded values (все через config)
10. ✅ Docker image size < 2GB

## Performance Targets
- Обработка 1MB markdown файла: < 2 минуты
- Startup time для всех сервисов: < 60 секунд
- Entity extraction accuracy: > 85%
- Relationship detection accuracy: > 75%
- Memory usage: < 4GB during processing

## Validation Commands
```bash
# Test infrastructure
docker-compose up -d
docker-compose ps  # All services healthy

# Test application  
docker-compose exec app pytest tests/ -v --cov=src --cov-report=html

# Test UI (доступен на http://localhost:8501)
open http://localhost:8501
# Upload sample MD files, verify processing

# Test agents
docker-compose exec app python -m src.agents.crew --test

# Performance test
docker-compose exec app python -m tests.performance.test_batch_processing
```

## Success Metrics
1. All 22 tasks completed ✅
2. All tests passing ✅
3. Sample data processing successfully ✅
4. **Chat functionality working with source citations** ✅
5. Documentation complete ✅
6. Docker deployment working within 32GB RAM ✅

## Risk Mitigation
- **LLM failures**: Retry logic с exponential backoff
- **Memory issues**: Streaming processing для больших файлов
- **Database connection**: Connection pooling и reconnection
- **UI responsiveness**: Async processing с progress updates
- **Model loading**: Health checks до начала обработки