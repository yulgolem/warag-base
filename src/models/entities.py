from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Entity(BaseModel):
    """Represents an extracted entity."""

    id: Optional[str] = None
    name: str
    type: str
    description: Optional[str] = None
    source_file: str
    chunk_id: str
    confidence: float
