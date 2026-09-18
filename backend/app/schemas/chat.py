import uuid

from pydantic import BaseModel


class SourceRef(BaseModel):
    document_path: str
    snippet: str
    score: float


class ChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    sources: list[SourceRef]

