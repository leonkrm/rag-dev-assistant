import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceCreate(BaseModel):
    name: str
    type: str  # "git" | "local_folder" | "upload"
    uri: str


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    uri: str
    status: str
    created_at: datetime


class SearchResultItem(BaseModel):
    document_path: str
    chunk_content: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
