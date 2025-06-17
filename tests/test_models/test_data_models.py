from pydantic import ValidationError

from src.models.entities import Entity
from src.models.relationships import Relationship


def test_entity_model_fields():
    entity = Entity(
        id="1",
        name="John",
        type="person",
        description="Hero",
        source_file="story.md",
        chunk_id="c1",
        confidence=0.95,
    )

    assert entity.id == "1"
    assert entity.name == "John"
    assert entity.type == "person"
    assert entity.description == "Hero"
    assert entity.source_file == "story.md"
    assert entity.chunk_id == "c1"
    assert entity.confidence == 0.95


def test_entity_optional_fields_defaults():
    entity = Entity(
        name="Sword",
        type="object",
        source_file="story.md",
        chunk_id="c2",
        confidence=0.8,
    )

    assert entity.id is None
    assert entity.description is None


def test_relationship_model_fields():
    rel = Relationship(
        source_entity="John",
        target_entity="Mary",
        relation_type="friend",
        description="Childhood friends",
        confidence=0.9,
    )

    assert rel.source_entity == "John"
    assert rel.target_entity == "Mary"
    assert rel.relation_type == "friend"
    assert rel.description == "Childhood friends"
    assert rel.confidence == 0.9


def test_relationship_missing_required():
    try:
        Relationship(source_entity="A", target_entity="B")
    except ValidationError:
        pass
    else:
        raise AssertionError("ValidationError not raised")
