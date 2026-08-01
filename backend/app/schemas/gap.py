import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ResearchGapResponse(BaseModel):
    id: int
    topic_id: int
    topic_name: str
    description: str
    missing_methodology: Optional[str] = None
    missing_dataset: Optional[str] = None
    missing_hardware: Optional[str] = None
    missing_model: Optional[str] = None
    innovation_score: float
    detected_at: datetime.datetime

    class Config:
        from_attributes = True

class ResearchIdeaResponse(BaseModel):
    id: int
    gap_id: Optional[int] = None
    title: str
    description: str
    type: str  # IEEE, SIH, Patent, Startup
    target_audience: Optional[str] = None
    roadmap_steps: Optional[List[Dict[str, Any]]] = None
    novelty_score: float
    generated_at: datetime.datetime

    class Config:
        from_attributes = True

class LiteratureReviewRequest(BaseModel):
    topic_name: str

class LiteratureReviewResponse(BaseModel):
    title: str
    topic_name: str
    markdown_content: str
    created_at: datetime.datetime
