# Assistant Memory

## Project Overview
- Мультиагентная система помощи писателю
- Текущая фаза: Phase 1 (MVP) - World Knowledge Graph
- Основная цель: Извлечение сущностей из MD файлов, построение графа связей, векторный поиск

## Infrastructure
- Docker Compose с 4 сервисами:
  1. PostgreSQL (pgvector) - для векторного поиска
  2. Neo4j - для графа знаний
  3. Ollama - для локальных LLM
  4. Streamlit app - веб-интерфейс

## AI Models
- NuExtract - для извлечения сущностей (загружена)
- ilyagusev/saiga_llama3 - для анализа связей (загружена)
- Модели хранятся в именованном томе `ollama_models`

## Recent Changes
- Добавлена поддержка GPU для Ollama
- Настроено сохранение моделей между перезапусками
- Обновлена модель Saiga на ilyagusev/saiga_llama3

## Current Tasks
- Task 9 (Entity Extractor Agent) - завершен
- Task 10 (Relationship Analyzer Agent) - в процессе

## Important Paths
- Streamlit UI: http://localhost:8501
- Neo4j Browser: http://localhost:7474
- Ollama API: http://localhost:11434

## Credentials
- Neo4j: neo4j/worldbuilding123
- PostgreSQL: postgres/postgres

## Development Notes
- Используется Python 3.11
- Основные зависимости: CrewAI, Streamlit, Neo4j, pgvector
- Все сервисы запускаются через Docker Compose
- Модели Ollama сохраняются в именованном томе 