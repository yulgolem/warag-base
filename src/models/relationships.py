from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Relationship(BaseModel):
    """Represents a relationship between entities."""

    source_entity: str
    target_entity: str
    relation_type: str
    description: Optional[str] = None
    confidence: float
