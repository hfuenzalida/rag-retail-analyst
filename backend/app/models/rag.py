"""RAG-related Pydantic models."""

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DocFilters(BaseModel):
    client_id: str
    doc_type: Optional[Literal["report", "playbook", "note", "schema"]] = None
    date_range: Optional[tuple[date, date]] = None


class DocChunk(BaseModel):
    id: int
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str


class IngestDocumentRequest(BaseModel):
    client_id: str
    content: str
    doc_type: Literal["report", "playbook", "note", "schema"] = "note"
    title: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class IngestDocumentResponse(BaseModel):
    chunks_created: int
    document_ids: list[int]
