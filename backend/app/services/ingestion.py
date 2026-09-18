"""
Индексация источников знаний.

Реализована индексация из локальной папки. Для git-репозиториев — TODO ниже
с описанием, как расширить.
"""
import hashlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Chunk, Document, Source
from app.services.chunking import split_into_chunks
from app.services.embeddings import embed_texts

SUPPORTED_EXTENSIONS = {".py", ".ts", ".md", ".yml", ".yaml", ".txt", ".json"}


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def index_local_folder(db: AsyncSession, source: Source, folder_path: str) -> int:
    """Индексирует все поддерживаемые файлы из локальной папки."""
    root = Path(folder_path)
    if not root.exists():
        raise FileNotFoundError(f"Папка не найдена: {folder_path}")

    indexed = 0
    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        text = file_path.read_text(encoding="utf-8", errors="ignore")
        content_hash = _hash_content(text)
        relative_path = str(file_path.relative_to(root))

        document = Document(
            source_id=source.id,
            path=relative_path,
            title=file_path.name,
            content_hash=content_hash,
        )
        db.add(document)
        await db.flush()

        chunks_text = split_into_chunks(text)
        if not chunks_text:
            continue

        embeddings = embed_texts(chunks_text)
        for idx, (chunk_text, vector) in enumerate(zip(chunks_text, embeddings)):
            db.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=idx,
                    content=chunk_text,
                    embedding=vector,
                )
            )
        indexed += 1

    await db.commit()
    return indexed


# TODO: index_git_repository(db, source, repo_url, branch="main")
#   1. git clone --depth 1 <repo_url> во временную директорию.
#   2. Обойти файлы так же, как в index_local_folder.
#   3. Сравнивать content_hash для инкрементальной переиндексации.
#   4. Удалять из БД документы, которых больше нет в репозитории.
#   5. Запускать в фоне (BackgroundTasks / Celery / RQ).
