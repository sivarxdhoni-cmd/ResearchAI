import datetime
from typing import Optional, List
from pydantic import BaseModel

class PaperBase(BaseModel):
    title: str
    authors_text: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    publication_year: Optional[int] = None
    conference_journal: Optional[str] = None
    doi: Optional[str] = None
    arxiv_url: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperResponse(PaperBase):
    id: int
    upload_date: datetime.datetime
    status: str
    pdf_path: Optional[str] = None

    class Config:
        from_attributes = True

class PaperDetailResponse(PaperResponse):
    methodology: Optional[str] = None
    dataset_names: Optional[str] = None
    algorithms_used: Optional[str] = None
    accuracy_results: Optional[str] = None
    limitations: Optional[str] = None
    future_work: Optional[str] = None
    conclusion: Optional[str] = None

    class Config:
        from_attributes = True

class PaperCompareRequest(BaseModel):
    paper_ids: List[int]

class PaperComparisonItem(BaseModel):
    id: int
    title: str
    authors: str
    year: int
    methodology: str
    datasets: List[str]
    algorithms: List[str]
    metrics: List[str]
    limitations: str
    future_work: str

class PaperComparisonMatrix(BaseModel):
    comparison_data: List[PaperComparisonItem]
