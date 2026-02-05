from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from uuid import UUID

class QAFilters(BaseModel):
    doc_name: Optional[str] = Field(None, description="검색 범위를 제한할 문서 이름")

class UserProfile(BaseModel):
    name: Optional[str] = Field(None, description="사용자 이름")
    role: Optional[str] = Field(None, description="직업 또는 역할")
    interests: Optional[List[str]] = Field(None, description="관심 분야")
    custom_instructions: Optional[str] = Field(None, description="추가 지시 사항 (예: 항상 친절하게, 전문 용어 사용 자제 등)")

class QARequest(BaseModel):
    query: str
    session_id: Optional[str] = Field(None, description="채팅 세션 ID (없으면 새 세션 생성)")
    history: Optional[List[Dict[str, str]]] = Field(None, description="이전 대화 내역 ( [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}] )")
    user_profile: Optional[UserProfile] = Field(None, description="사용자 개인화 프로필 정보")
    filters: Optional[QAFilters] = None

class QAResponse(BaseModel):
    answer: str
    retrieved_images: List[str]
    doc_name: Optional[str] = None
    page: Optional[int] = None
    session_id: str = Field(..., description="현재 채팅 세션 ID")
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
class ChatSession(BaseModel):
    session_id: str
    title: str
    created_at: str
    last_message_at: str

class SessionListResponse(BaseModel):
    sessions: List[ChatSession]

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    trace_id: Optional[str] = None

class SessionDetailResponse(BaseModel):
    session_id: str
    title: str
    messages: List[ChatMessage]
