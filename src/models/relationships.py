from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class Relationship(BaseModel):
    """Data model representing a relationship between two entities."""

    source_entity: str
    target_entity: str
    relation_type: str
    description: Optional[str]
    confidence: float
