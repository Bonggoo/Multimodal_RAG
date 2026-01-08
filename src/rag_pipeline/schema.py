from typing import List, Optional
from pydantic import BaseModel, Field

class Image(BaseModel):
    description: str
    caption: Optional[str] = None

class PageContent(BaseModel):
    text: str
    tables: List[str]
    images: List[Image]
    chapter_path: Optional[str] = None
    keywords: List[str] = Field(default_factory=list, description="페이지의 핵심 기술 용어 및 키워드 리스트")
    summary: Optional[str] = Field(None, description="페이지의 내용을 요약한 텍스트")
    document_title: Optional[str] = Field(None, description="문서의 제목 (표지나 헤더에서 추출)")
