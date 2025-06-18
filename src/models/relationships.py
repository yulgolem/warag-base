from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class Relationship:
    """Model representing a relationship between two entities."""
    source_entity: str
    target_entity: str
    relation_type: str
    description: str
    confidence: float
    source_text: str
    
    def __post_init__(self):
        """Validate the relationship data after initialization."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
            
        if not self.source_entity or not self.target_entity:
            raise ValueError("Source and target entities cannot be empty")
            
        if not self.relation_type:
            raise ValueError("Relation type cannot be empty")
            
        if not self.description:
            raise ValueError("Description cannot be empty")
            
        if not self.source_text:
            raise ValueError("Source text cannot be empty")
            
    def to_dict(self) -> dict:
        """Convert relationship to dictionary."""
        return {
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "relation_type": self.relation_type,
            "description": self.description,
            "confidence": self.confidence,
            "source_text": self.source_text
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Relationship':
        """Create relationship from dictionary."""
        return cls(
            source_entity=data["source_entity"],
            target_entity=data["target_entity"],
            relation_type=data["relation_type"],
            description=data["description"],
            confidence=data["confidence"],
            source_text=data["source_text"]
        )
