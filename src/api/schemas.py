from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID

class QAFilters(BaseModel):
    doc_name: Optional[str] = Field(None, description="검색 범위를 제한할 문서 이름")

class QARequest(BaseModel):
    query: str
    filters: Optional[QAFilters] = None

class QAResponse(BaseModel):
    answer: str
    retrieved_images: List[str]
    doc_name: Optional[str] = None
    page: Optional[int] = None
    trace_id: Optional[UUID] = None  # 추적을 위한 고유 ID

class FeedbackRequest(BaseModel):
    trace_id: str = Field(..., description="피드백 대상 QA의 trace_id (UUID)")
    score: int = Field(..., description="1: 좋아요, -1: 싫어요")
    comment: Optional[str] = Field(None, description="추가 의견")

class AsyncIngestResponse(BaseModel):
    job_id: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None

class DocumentInfo(BaseModel):
    filename: str
    title: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]

class DeleteDocumentResponse(BaseModel):
    message: str
    deleted_db_entries: int
    thumbnail_deleted: bool
