"""Text chunking for RAG ingestion."""

from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    index: int


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[TextChunk]:
    """Split text into overlapping segments."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [TextChunk(content=cleaned, index=0)]

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(TextChunk(content=cleaned[start:end], index=index))
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)
        index += 1
    return chunks
