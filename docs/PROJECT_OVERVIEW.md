# Worldbuilding Assistant: Project Overview & Roadmap

## Vision
Комплексный ИИ-ассистент для писателей, автоматизирующий создание и поддержку консистентности художественных миров через анализ текстов, построение графов знаний и контроль логических связей.

## Target Workflow
```
Мироустройство → Сюжетное ядро → Структура → Детализация → Написание
     ↓              ↓              ↓           ↓           ↓
  Концепции     Конфликты      Архитектура  Персонажи   Контроль
   Локации      События         Хронология   Сцены     Консистентности
```

## Development Phases

### 🚀 Phase 1: MVP - World Knowledge Graph (Current)
**Цель**: Базовый ассистент мироустройства  
**Функции**:
- Извлечение сущностей из MD файлов (персонажи, локации, концепции)
- Построение графа связей между сущностями
- Векторный поиск по семантике и ключевым словам
- **Chat с WorldBuildingAgent** для вопросов о загруженных сущностях
- Web UI для загрузки файлов и просмотра результатов

**Технологии**: CrewAI, Neo4j, PostgreSQL+pgvector, Streamlit, Ollama  
**Срок**: 3-4 недели  
**Результат**: Docker-приложение с базовой обработкой текстов + чат

### 🎯 Phase 2: Consistency Control System
**Цель**: Автоматический контроль консистентности мира  
**Новые агенты**:
- **ConsistencyCheckerAgent** - обнаружение противоречий в описаниях сущностей
- **TimelineValidatorAgent** - проверка временной логики событий
- **GeographyValidatorAgent** - проверка географической логики локаций
- **CharacterConsistencyAgent** - контроль характеристик персонажей
- **ConflictResolverAgent** - предложения исправлений противоречий

**Технологии**: Temporal reasoning, Logic programming, Rule-based systems
**Срок**: 2-3 недели  

### 📖 Phase 3: Writing Assistant Integration  
**Цель**: Помощь в процессе написания текста  
**Новые агенты**:
- **AtmosphereAnalyzerAgent** - анализ атмосферы и тональности повествования
- **PacingControllerAgent** - контроль пейсинга и структуры сцен
- **FlashbackTrackerAgent** - отслеживание флэшбеков и предчувствий
- **StoryArcAgent** - анализ "вертикальных историй" персонажей
- **DetailSuggesterAgent** - генерация атмосферных деталей

**Технологии**: Sentiment analysis, Narrative structure analysis, Scene analysis
**Срок**: 3-4 недели  

### 🎭 Phase 4: Character & Style Profiling
**Цель**: Формирование уникальных речевых и стилистических профилей  
**Новые агенты**:
- **SpeechPatternAgent** - анализ речевых паттернов персонажей
- **WorldLanguageAgent** - создание языкового паспорта мира
- **StyleConsistencyAgent** - детекция стилистических несоответствий
- **StyleGeneratorAgent** - генерация текста в установленном стиле
- **ToneAdapterAgent** - адаптация тона повествования

**Технологии**: Style transfer, Speaker identification, Linguistic analysis
**Срок**: 4-5 недель  

### 🧠 Phase 5: Advanced Story Architecture
**Цель**: Помощь в структурировании сложных нарративов  
**Новые агенты**:
- **PlotCoreAgent** - формирование сюжетного ядра из концепций
- **ConflictAnalyzerAgent** - анализ конфликтов и их развития
- **StructureOptimizerAgent** - оптимизация структуры произведения
- **MultiPlotAgent** - планирование многоуровневых сюжетных линий
- **AlternativeGeneratorAgent** - генерация альтернативных развитий

**Технологии**: Story generation, Plot analysis, Narrative planning, Causal reasoning
**Срок**: 5-6 недель  

### 🚀 Phase 6: Full Writing Companion
**Цель**: Интегрированная среда написания с ИИ-поддержкой  
**Новые агенты**:
- **RealTimeWritingAgent** - анализ и предложения при написании
- **VersionControlAgent** - управление версиями и альтернативами
- **EditorAgent** - редакторские рекомендации и исправления
- **FormatExportAgent** - экспорт в различные форматы
- **WorkflowOrchestratorAgent** - координация всех агентов

**Технологии**: Real-time NLP, Version control, Multi-format generation
**Срок**: 6-8 недель  

## Agent System Evolution

### MVP Agent (Phase 1)
```
WorldKnowledgeAgent
├── EntityExtractorAgent (NuExtract)
├── RelationshipAnalyzerAgent (Saiga)
├── GraphCoordinatorAgent (Neo4j + pgvector)
└── ChatAgent (RAG на основе графа + векторного поиска)
```

### Multi-Agent System (Phase 6)
```
WritingWorkflowOrchestrator
├── WorldBuilding/
│   ├── EntityExtractorAgent
│   ├── RelationshipAnalyzerAgent
│   └── GraphCoordinatorAgent
├── Consistency/
│   ├── ConsistencyCheckerAgent
│   ├── TimelineValidatorAgent
│   ├── GeographyValidatorAgent
│   └── ConflictResolverAgent
├── Writing/
│   ├── AtmosphereAnalyzerAgent
│   ├── PacingControllerAgent
│   ├── FlashbackTrackerAgent
│   └── DetailSuggesterAgent
├── Style/
│   ├── SpeechPatternAgent
│   ├── StyleConsistencyAgent
│   └── ToneAdapterAgent
└── Architecture/
    ├── PlotCoreAgent
    ├── StructureOptimizerAgent
    └── AlternativeGeneratorAgent
```

## Success Metrics by Phase

| Phase | Key Metrics | Target Values |
|-------|-------------|---------------|
| MVP | Entity extraction accuracy, Graph completeness | >85%, >80% |
| Phase 2 | Contradiction detection rate, False positives | >90%, <10% |
| Phase 3 | Writing quality improvement, User satisfaction | +25%, >8.5/10 |
| Phase 4 | Style consistency score, Character voice accuracy | >90%, >85% |
| Phase 5 | Plot coherence rating, Structure optimization | >8.5/10, +30% |
| Phase 6 | User retention, Writing productivity gain | >80%, +50% |

## Technical Architecture

### Infrastructure Requirements by Phase
| Phase | CPU Cores | RAM | Storage | GPU | Key Components |
|-------|-----------|-----|---------|-----|----------------|
| MVP | 4-8 | 16-24GB | 100GB | Optional | Basic agents, Neo4j, PostgreSQL |
| Phase 2-3 | 8-12 | 24-32GB | 200GB | Optional | Logic engines, temporal reasoning |
| Phase 4-6 | 8-16 | 32GB | 500GB | Recommended | Style models, real-time processing |

**Constraint**: Максимум 32GB RAM - оптимизация для ограниченного железа

### Risk Assessment & Mitigation

**Technical Risks**:
- **LLM Quality**: Local models vs API cost trade-off → Hybrid approach with fallback
- **Scalability**: Graph DB performance with large knowledge bases → Incremental indexing
- **Accuracy**: NER and relationship extraction quality in Russian → Model fine-tuning
- **Integration**: Multi-agent coordination complexity → Modular architecture

**Development Strategy**:
- Incremental development with constant testing
- Domain-specific model optimization  
- Modular architecture with clear interfaces
- Comprehensive test coverage (80%+)
