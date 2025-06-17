from __future__ import annotations

from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config.settings import settings


def chunk_markdown(text: str, file_name: str) -> List[Dict[str, str]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    result = []
    for idx, chunk in enumerate(chunks):
        result.append({
            "chunk_id": f"{file_name}_{idx}",
            "text": chunk,
            "tokens_count": len(chunk.split()),
            "file_name": file_name,
        })
    return result
