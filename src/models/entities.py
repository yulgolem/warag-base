from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class Entity(BaseModel):
    """Data model representing an extracted entity."""

    id: Optional[str]
    name: str
    type: str
    description: Optional[str]
    source_file: str
    chunk_id: str
    confidence: float
