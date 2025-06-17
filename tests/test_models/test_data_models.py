from src.models.entities import Entity
from src.models.relationships import Relationship


def test_entity_model():
    entity = Entity(
        id="1",
        name="Alice",
        type="person",
        description="Protagonist",
        source_file="story.md",
        chunk_id="chunk1",
        confidence=0.9,
    )
    assert entity.name == "Alice"
    assert entity.type == "person"


def test_relationship_model():
    rel = Relationship(
        source_entity="Alice",
        target_entity="Bob",
        relation_type="knows",
        description="Friends",
        confidence=0.8,
    )
    assert rel.relation_type == "knows"
    assert rel.source_entity == "Alice"
