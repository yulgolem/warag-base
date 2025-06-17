from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Entity(BaseModel):
    """Represents an extracted entity."""

    id: Optional[str] = None
    name: str
    type: str
    description: Optional[str] = None
    mentions: List[str] = []
    confidence: float
    source_file: str
    chunk_id: str
    source_chunk: str
    context: str
