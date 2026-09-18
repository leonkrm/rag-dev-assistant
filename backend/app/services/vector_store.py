"""
Векторный поиск по таблице chunks через pgvector.
Используем оператор косинусного расстояния `<=>`.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.document import Chunk, Document


async def similarity_search(
    db: AsyncSession, query_embedding: list[float], top_k: int = 5
) -> list[tuple[Chunk, Document, float]]:
    """
    Возвращает top_k наиболее похожих чанков вместе с их документами и
    оценкой похожести (чем меньше расстояние, тем больше похожесть).
    """
    distance = Chunk.embedding.cosine_distance(query_embedding).label("distance")

    stmt = (
        select(Chunk, distance)
        .options(joinedload(Chunk.document))
        .order_by(distance)
        .limit(top_k)
    )
    result = await db.execute(stmt)
    rows = result.all()

    output: list[tuple[Chunk, Document, float]] = []
    for chunk, dist in rows:
        similarity = 1 - float(dist)
        output.append((chunk, chunk.document, similarity))
    return output
