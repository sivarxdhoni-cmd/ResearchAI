from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.db.models import User, ChatHistory
from backend.app.schemas.chat import ChatRequest, ChatResponse
from rag.search import RAGEngine

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def ask_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Initialize RAG engine
        rag = RAGEngine()
        
        # Execute query
        result = rag.query(request.message)
        
        # Save to database history
        chat_entry = ChatHistory(
            user_id=current_user.id,
            message=request.message,
            response=result["answer"],
            sources=result["sources"]
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)

        return ChatResponse(
            id=chat_entry.id,
            message=chat_entry.message,
            response=chat_entry.response,
            sources=result["sources"],
            timestamp=chat_entry.timestamp
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Chat assistant failed: {e}"
        )

@router.get("/history", response_model=list[ChatResponse])
def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(ChatHistory)\
        .filter(ChatHistory.user_id == current_user.id)\
        .order_by(ChatHistory.timestamp.asc())\
        .limit(limit).all()
    return history
