"""Управление источниками знаний: создание, синхронизация (индексация), список."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Source
from app.schemas.document import SourceCreate, SourceOut
from app.services.ingestion import index_local_folder

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=SourceOut, status_code=201)
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    source = Source(name=payload.name, type=payload.type, uri=payload.uri, status="pending")
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.post("/{source_id}/sync", status_code=202)
async def sync_source(source_id: str, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if source is None:
        raise HTTPException(404, "Источник не найден")

    if source.type != "local_folder":
        raise HTTPException(400, f"Индексация типа '{source.type}' пока не реализована")

    source.status = "indexing"
    await db.commit()

    try:
        count = await index_local_folder(db, source, source.uri)
        source.status = "ready"
        await db.commit()
        return {"indexed_documents": count, "status": source.status}
    except Exception as exc:
        source.status = "error"
        await db.commit()
        raise HTTPException(500, f"Ошибка индексации: {exc}") from exc
