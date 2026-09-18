"""Простое разбиение текста на чанки фиксированного размера с перекрытием."""
from app.core.config import get_settings

settings = get_settings()


def split_into_chunks(text: str) -> list[str]:
    size = settings.RAG_CHUNK_SIZE
    overlap = settings.RAG_CHUNK_OVERLAP
    if len(text) <= size:
        return [text] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks
