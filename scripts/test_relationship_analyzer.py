# Интеграционный тест с реальной моделью Saiga больше не используется.
# Для проверки целостности кода используйте unit-тесты с моками:
# pytest tests/test_agents/test_relationship_analyzer.py

from src.agents.relationship_analyzer import RelationshipAnalyzerAgent
from src.models.entities import Entity

def main():
    # Создаем тестовые сущности
    entities = [
        Entity(
            name="Гарри Поттер",
            type="person",
            description="Главный герой",
            mentions=["Гарри", "Гарри Поттер"],
            confidence=0.95,
            source_file="test.md",
            chunk_id="chunk1",
            source_chunk="test_chunk",
            context="Гарри Поттер учился в школе магии"
        ),
        Entity(
            name="Хогвартс",
            type="organization",
            description="Школа магии и волшебства",
            mentions=["Хогвартс", "школа Хогвартс"],
            confidence=0.9,
            source_file="test.md",
            chunk_id="chunk1",
            source_chunk="test_chunk",
            context="школа магии Хогвартс"
        ),
        Entity(
            name="Лондон",
            type="location",
            description="Столица Великобритании",
            mentions=["Лондон"],
            confidence=0.95,
            source_file="test.md",
            chunk_id="chunk1",
            source_chunk="test_chunk",
            context="недалеко от Лондона"
        )
    ]

    # Текст для анализа
    text = "Гарри Поттер учился в школе магии Хогвартс, которая находится недалеко от Лондона."

    # Создаем агент
    analyzer = RelationshipAnalyzerAgent()

    print("Анализируем отношения между сущностями...")
    print(f"Текст: {text}")
    print("\nСущности:")
    for entity in entities:
        print(f"- {entity.name} ({entity.type})")

    # Анализируем отношения
    relationships = analyzer.analyze_relationships(entities, text)

    print("\nНайденные отношения:")
    for rel in relationships:
        print(f"\nОтношение: {rel.source_entity} -> {rel.target_entity}")
        print(f"Тип: {rel.relation_type}")
        print(f"Описание: {rel.description}")
        print(f"Уверенность: {rel.confidence}")
        print(f"Подтверждающий текст: {rel.source_text}")

if __name__ == "__main__":
    main() 