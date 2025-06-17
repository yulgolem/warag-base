from __future__ import annotations

from typing import List, Dict, Optional

import tiktoken


DEFAULT_SEPARATORS = ["\n\n", "\n", ".", "!", "?", ";", " "]


def recursive_chunk_text(
    text: str,
    file_name: Optional[str] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    separators: Optional[List[str]] = None,
) -> List[Dict]:
    """Recursively split text and add overlap, returning chunk metadata."""
    if not text or not text.strip():
        return []

    if separators is None:
        separators = DEFAULT_SEPARATORS.copy()

    tokenizer = tiktoken.get_encoding("cl100k_base")

    text_chunks = _recursive_split(text, separators, chunk_size, tokenizer)
    overlapped = _add_overlap(text_chunks, chunk_overlap, tokenizer)

    result: List[Dict] = []
    for i, chunk_text in enumerate(overlapped):
        result.append(
            {
                "chunk_id": f"chunk_{i}",
                "file_name": file_name or "",
                "text": chunk_text.strip(),
                "tokens_count": len(tokenizer.encode(chunk_text)),
            }
        )
    return result


def _split_by_separator(text: str, separator: str) -> List[str]:
    """Split text by a separator, keeping it attached to previous segment."""
    if separator not in text:
        return [text]

    parts = text.split(separator)
    result: List[str] = []
    for part in parts[:-1]:
        result.append(part + separator)
    if parts[-1]:
        result.append(parts[-1])
    return result


def _hard_split_by_tokens(text: str, max_tokens: int, tokenizer) -> List[str]:
    """Fallback splitting by exact token count."""
    tokens = tokenizer.encode(text)
    chunks: List[str] = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks


def _recursive_split(text: str, separators: List[str], max_tokens: int, tokenizer) -> List[str]:
    """Recursively split text using separators hierarchy."""
    if len(tokenizer.encode(text)) <= max_tokens:
        return [text] if text.strip() else []

    if not separators:
        return _hard_split_by_tokens(text, max_tokens, tokenizer)

    current_sep = separators[0]
    remaining = separators[1:]

    parts = _split_by_separator(text, current_sep)
    if len(parts) == 1:
        return _recursive_split(text, remaining, max_tokens, tokenizer)

    result: List[str] = []
    for part in parts:
        if not part.strip():
            continue
        if len(tokenizer.encode(part)) > max_tokens:
            result.extend(_recursive_split(part, remaining, max_tokens, tokenizer))
        else:
            result.append(part)
    return result


def _add_overlap(chunks: List[str], overlap_tokens: int, tokenizer) -> List[str]:
    """Add token overlap between adjacent chunks."""
    if len(chunks) <= 1 or overlap_tokens == 0:
        return chunks

    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_chunk = chunks[i - 1]
        current_chunk = chunks[i]

        prev_tokens = tokenizer.encode(prev_chunk)
        if len(prev_tokens) >= overlap_tokens:
            overlap_text = tokenizer.decode(prev_tokens[-overlap_tokens:])
            new_chunk = overlap_text + current_chunk
        else:
            new_chunk = prev_chunk + current_chunk
        overlapped.append(new_chunk)
    return overlapped
