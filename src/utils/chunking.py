from __future__ import annotations

from typing import List, Dict
from src.config.settings import Settings, ENV_FILE


def chunk_markdown(text: str, file_name: str) -> List[Dict[str, str]]:
    settings = Settings(_env_file=ENV_FILE)
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    result: List[Dict[str, str]] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunk = text[start:end]
        result.append({
            "chunk_id": f"{file_name}_{idx}",
            "text": chunk,
            "tokens_count": len(chunk.split()),
            "file_name": file_name,
        })
        start += size - overlap
        idx += 1
    return result
