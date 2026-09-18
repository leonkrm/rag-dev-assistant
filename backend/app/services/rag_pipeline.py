"""
Ядро проекта: RAG-пайплайн.

Шаги:
    1. Получаем вопрос пользователя.
    2. Превращаем вопрос в эмбеддинг.
    3. Ищем top_k наиболее похожих чанков в pgvector.
    4. Собираем из них контекст с указанием источников.
    5. Формируем промпт и вызываем LLM.
    6. Возвращаем ответ + список источников (для цитирования в UI).
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.schemas.chat import SourceRef
from app.services.embeddings import embed_query
from app.services.llm_client import get_llm_client
from app.services.vector_store import similarity_search

settings = get_settings()

SYSTEM_PROMPT = """Ты — ассистент разработчика. Отвечай на вопросы только на основе
предоставленного контекста из кодовой базы и документации проекта.
Если в контексте недостаточно информации — честно скажи об этом, не выдумывай.
Отвечай кратко и по делу, при необходимости приводи фрагменты кода."""


def _build_context(chunks: list) -> str:
    parts = []
    for i, (chunk, document, score) in enumerate(chunks, start=1):
        parts.append(f"[Источник {i}: {document.path} | релевантность={score:.2f}]\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


def _build_user_prompt(question: str, context: str) -> str:
    return f"""Контекст из кодовой базы/документации проекта:

{context}

Вопрос пользователя: {question}

Ответь на вопрос, опираясь на контекст выше. Если использовал конкретный источник,
упоминай его номер (например, "как видно в [Источник 2]")."""


async def answer_question(db: AsyncSession, question: str) -> tuple[str, list[SourceRef]]:
    query_embedding = embed_query(question)
    results = await similarity_search(db, query_embedding, top_k=settings.RAG_TOP_K)

    if not results:
        return (
            "В базе знаний пока нет проиндексированных данных, чтобы ответить на этот "
            "вопрос. Сначала добавьте источник через /api/sources.",
            [],
        )

    context = _build_context(results)
    llm = get_llm_client()
    prompt = _build_user_prompt(question, context)
    answer = await llm.generate(SYSTEM_PROMPT, prompt)

    sources = [
        SourceRef(document_path=document.path, snippet=chunk.content[:300], score=round(score, 3))
        for chunk, document, score in results
    ]

    return answer, sources
