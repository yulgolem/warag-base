import pytest
from unittest.mock import patch, MagicMock
from src.agents.relationship_analyzer import RelationshipAnalyzerAgent
from src.models.entities import Entity
from src.models.relationships import Relationship

@pytest.fixture
def analyzer():
    return RelationshipAnalyzerAgent(ollama_base_url="http://test:11434")

@pytest.fixture
def sample_entities():
    return [
        Entity(name="Гарри Поттер", type="person", start_pos=0, end_pos=13),
        Entity(name="Хогвартс", type="organization", start_pos=25, end_pos=33),
        Entity(name="Лондон", type="location", start_pos=45, end_pos=51)
    ]

@pytest.fixture
def sample_text():
    return "Гарри Поттер учился в школе Хогвартс, которая находится недалеко от Лондона."

class TestRelationshipAnalyzerAgent:
    def test_analyze_relationships_success(self, analyzer, sample_entities, sample_text):
        mock_response = {
            "response": '''{
                "relationship": {
                    "source_entity": "Гарри Поттер",
                    "target_entity": "Хогвартс",
                    "relation_type": "part_of",
                    "description": "является учеником",
                    "confidence": 0.85,
                    "source_text": "Гарри Поттер учился в школе Хогвартс"
                }
            }'''
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            
            relationships = analyzer.analyze_relationships(sample_entities, sample_text)
            
            assert len(relationships) > 0
            rel = relationships[0]
            assert rel.source_entity == "Гарри Поттер"
            assert rel.target_entity == "Хогвартс"
            assert rel.relation_type == "part_of"
            assert rel.confidence >= 0.75

    def test_analyze_relationships_no_relation(self, analyzer, sample_entities, sample_text):
        mock_response = {
            "response": '''{
                "relationship": null
            }'''
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            
            relationships = analyzer.analyze_relationships(sample_entities, sample_text)
            assert len(relationships) == 0

    def test_entity_pair_generation(self, analyzer, sample_entities):
        pairs = analyzer._generate_entity_pairs(sample_entities)
        assert len(pairs) <= analyzer.max_pairs_per_chunk
        
        # Check that we don't have pairs of same type (except person-person)
        for entity1, entity2 in pairs:
            if entity1.type == entity2.type:
                assert entity1.type == "person"

    def test_confidence_filtering(self, analyzer, sample_entities, sample_text):
        mock_response = {
            "response": '''{
                "relationship": {
                    "source_entity": "Гарри Поттер",
                    "target_entity": "Хогвартс",
                    "relation_type": "part_of",
                    "description": "является учеником",
                    "confidence": 0.5,
                    "source_text": "Гарри Поттер учился в школе Хогвартс"
                }
            }'''
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            
            relationships = analyzer.analyze_relationships(
                sample_entities, 
                sample_text,
                confidence_threshold=0.75
            )
            assert len(relationships) == 0

    def test_batch_processing(self, analyzer):
        entities_batch = [
            [Entity(name="Гарри", type="person"), Entity(name="Хогвартс", type="organization")],
            [Entity(name="Рон", type="person"), Entity(name="Гермиона", type="person")]
        ]
        texts = [
            "Гарри учился в Хогвартсе",
            "Рон дружил с Гермионой"
        ]
        
        mock_responses = [
            {
                "response": '''{
                    "relationship": {
                        "source_entity": "Гарри",
                        "target_entity": "Хогвартс",
                        "relation_type": "part_of",
                        "description": "является учеником",
                        "confidence": 0.85,
                        "source_text": "Гарри учился в Хогвартсе"
                    }
                }'''
            },
            {
                "response": '''{
                    "relationship": {
                        "source_entity": "Рон",
                        "target_entity": "Гермиона",
                        "relation_type": "knows",
                        "description": "дружит с",
                        "confidence": 0.9,
                        "source_text": "Рон дружил с Гермионой"
                    }
                }'''
            }
        ]
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = [
                MagicMock(json=lambda: resp, raise_for_status=MagicMock())
                for resp in mock_responses
            ]
            
            results = analyzer.analyze_relationships_batch(entities_batch, texts)
            assert len(results) == 2
            assert len(results[0]) == 1
            assert len(results[1]) == 1

    def test_saiga_response_parsing(self, analyzer, sample_entities, sample_text):
        # Test with extra text after JSON
        mock_response = {
            "response": '''{
                "relationship": {
                    "source_entity": "Гарри Поттер",
                    "target_entity": "Хогвартс",
                    "relation_type": "part_of",
                    "description": "является учеником",
                    "confidence": 0.85,
                    "source_text": "Гарри Поттер учился в школе Хогвартс"
                }
            }
            Это дополнительный текст, который должен быть проигнорирован'''
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            
            relationships = analyzer.analyze_relationships(sample_entities, sample_text)
            assert len(relationships) == 1

    def test_russian_text_analysis(self, analyzer):
        entities = [
            Entity(name="Иван", type="person"),
            Entity(name="Москва", type="location")
        ]
        text = "Иван живет в Москве"
        
        mock_response = {
            "response": '''{
                "relationship": {
                    "source_entity": "Иван",
                    "target_entity": "Москва",
                    "relation_type": "located_in",
                    "description": "проживает в",
                    "confidence": 0.9,
                    "source_text": "Иван живет в Москве"
                }
            }'''
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            
            relationships = analyzer.analyze_relationships(entities, text)
            assert len(relationships) == 1
            assert relationships[0].relation_type == "located_in"

    def test_pair_prioritization(self, analyzer):
        entities = [
            Entity(name="Гарри", type="person"),
            Entity(name="Хогвартс", type="organization"),
            Entity(name="Лондон", type="location")
        ]
        text = "Гарри учился в Хогвартсе. Лондон далеко."
        
        pairs = analyzer._generate_entity_pairs(entities)
        prioritized = analyzer._prioritize_entity_pairs(pairs, text)
        
        # First pair should be Гарри-Хогвартс as they are closer in text
        first_pair = prioritized[0]
        assert first_pair[0].name == "Гарри"
        assert first_pair[1].name == "Хогвартс"

    def test_large_entity_set(self, analyzer):
        # Create 15 entities
        entities = [
            Entity(name=f"Entity{i}", type="person" if i % 2 == 0 else "location")
            for i in range(15)
        ]
        text = " ".join(entity.name for entity in entities)
        
        # Should limit to max_pairs_per_chunk pairs
        pairs = analyzer._generate_entity_pairs(entities)
        assert len(pairs) <= analyzer.max_pairs_per_chunk 