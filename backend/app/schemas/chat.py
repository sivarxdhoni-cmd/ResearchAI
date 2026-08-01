import datetime
from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatSource(BaseModel):
    paper_id: int
    title: str
    section: str
    text: str
    relevance_score: float

class ChatResponse(BaseModel):
    id: Optional[int] = None
    message: str
    response: str
    sources: List[ChatSource]
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
