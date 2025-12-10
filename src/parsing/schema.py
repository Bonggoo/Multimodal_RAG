from typing import List, Optional
from pydantic import BaseModel

class Image(BaseModel):
    description: str
    caption: Optional[str] = None

class PageContent(BaseModel):
    text: str
    tables: List[str]
    images: List[Image]
    chapter_path: Optional[str] = None
