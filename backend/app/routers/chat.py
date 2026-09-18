"""Чат-эндпоинт: вопрос пользователя -> RAG-пайплайн -> ответ + источники."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import answer_question

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    if payload.conversation_id:
        conversation = await db.get(Conversation, payload.conversation_id)
        if conversation is None:
            raise HTTPException(404, "Диалог не найден")
    else:
        conversation = Conversation(title=payload.message[:60])
        db.add(conversation)
        await db.flush()

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.message))

    try:
        answer, sources = await answer_question(db, payload.message)
    except Exception as exc:
        raise HTTPException(502, f"Ошибка при обращении к LLM: {exc}") from exc

    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            sources=[s.model_dump() for s in sources],
        )
    )
    await db.commit()

    return ChatResponse(conversation_id=conversation.id, answer=answer, sources=sources)
