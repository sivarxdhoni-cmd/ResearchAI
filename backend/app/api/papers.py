import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Form, status
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import get_current_user, RoleChecker
from backend.app.db.session import get_db
from backend.app.db.models import Paper, User
from backend.app.schemas.paper import (
    PaperResponse, PaperDetailResponse, PaperCompareRequest, 
    PaperComparisonItem, PaperComparisonMatrix
)
from backend.app.services.paper_processor import process_paper_background

router = APIRouter()

# Allow Scholars, Professors, Labs, and Admins to upload papers
upload_permission = RoleChecker(["Research Scholar", "Professor", "Research Lab"])

@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_202_ACCEPTED)
def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    publication_year: Optional[int] = Form(None),
    conference_journal: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    arxiv_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(upload_permission)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are accepted."
        )

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save the file locally
    safe_filename = "".join([c if c.isalnum() or c in (".", "_", "-") else "_" for c in file.filename])
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to disk: {e}"
        )

    # Create paper record in DB with placeholder title (it will be parsed from PDF)
    db_paper = Paper(
        title=file.filename.rsplit(".", 1)[0].replace("_", " "),
        pdf_path=file_path,
        publication_year=publication_year,
        conference_journal=conference_journal,
        doi=doi,
        arxiv_url=arxiv_url,
        status="processing"
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)

    # Spawn background processing task
    background_tasks.add_task(process_paper_background, db_paper.id)

    return db_paper

@router.get("/", response_model=List[PaperResponse])
def list_papers(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Paper)
    if status:
        query = query.filter(Paper.status == status)
    return query.order_by(Paper.upload_date.desc()).all()

@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found."
        )
    return paper

@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(upload_permission)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found."
        )
        
    # Delete local file if it exists
    if paper.pdf_path and os.path.exists(paper.pdf_path):
        try:
            os.remove(paper.pdf_path)
        except Exception as e:
            # Log error but proceed with DB deletion
            pass
            
    db.delete(paper)
    db.commit()
    return None

@router.post("/compare", response_model=PaperComparisonMatrix)
def compare_papers(
    request: PaperCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    papers = db.query(Paper).filter(Paper.id.in_(request.paper_ids)).all()
    if not papers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No matching papers found for comparison."
        )

    comparison_items = []
    for paper in papers:
        # Convert comma-separated strings to lists
        datasets = [d.strip() for d in paper.dataset_names.split(",")] if paper.dataset_names else []
        algorithms = [a.strip() for a in paper.algorithms_used.split(",")] if paper.algorithms_used else []
        metrics = [m.strip() for m in paper.accuracy_results.split(",")] if paper.accuracy_results else []

        comparison_items.append(
            PaperComparisonItem(
                id=paper.id,
                title=paper.title,
                authors=paper.authors_text or "Unknown",
                year=paper.publication_year or 2026,
                methodology=paper.methodology or "No methodology extracted",
                datasets=datasets,
                algorithms=algorithms,
                metrics=metrics,
                limitations=paper.limitations or "No limitations identified",
                future_work=paper.future_work or "No future scope identified"
            )
        )

    return PaperComparisonMatrix(comparison_data=comparison_items)
