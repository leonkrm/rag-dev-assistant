"""Прямой векторный поиск по базе знаний (без генерации ответа LLM)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.document import SearchResponse, SearchResultItem
from app.services.embeddings import embed_query
from app.services.vector_store import similarity_search

router = APIRouter(prefix="/api/search", tags=["search"])
settings = get_settings()


@router.get("", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    embedding = embed_query(q)
    results = await similarity_search(db, embedding, top_k=settings.RAG_TOP_K)
    items = [
        SearchResultItem(document_path=doc.path, chunk_content=chunk.content, score=round(score, 3))
        for chunk, doc, score in results
    ]
    return SearchResponse(query=q, results=items)
