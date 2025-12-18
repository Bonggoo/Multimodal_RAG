from pydantic import BaseModel
from typing import List, Optional, Any

class QARequest(BaseModel):
    query: str

class QAResponse(BaseModel):
    answer: str
    image_paths: List[str]
    expanded_query: Optional[str] = None

class AsyncIngestResponse(BaseModel):
    job_id: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None
