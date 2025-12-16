from pydantic import BaseModel
from typing import List, Optional

class QARequest(BaseModel):
    query: str

class QAResponse(BaseModel):
    answer: str
    image_paths: List[str]
    expanded_query: Optional[str] = None

class IngestResponse(BaseModel):
    filename: str
    total_pages: int
    status: str
    message: str
