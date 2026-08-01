from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.db.models import Paper, Topic, Author, ResearchGap, ResearchIdea, User
from knowledge_graph import get_graph_service

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_papers = db.query(Paper).count()
    total_topics = db.query(Topic).count()
    total_authors = db.query(Author).count()
    total_gaps = db.query(ResearchGap).count()
    total_ideas = db.query(ResearchIdea).count()

    # Get topics count distribution for trending charts
    topics_list = db.query(Topic).all()
    topic_distribution = []
    for t in topics_list:
        topic_distribution.append({
            "name": t.name,
            "count": len(t.papers)
        })
    # Sort and return top 8
    topic_distribution = sorted(topic_distribution, key=lambda x: x["count"], reverse=True)[:8]

    # Get recent papers status
    recent_papers = db.query(Paper).order_by(Paper.upload_date.desc()).limit(5).all()
    recent_list = []
    for p in recent_papers:
        recent_list.append({
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "date": p.upload_date.strftime("%Y-%m-%d %H:%M")
        })

    return {
        "metrics": {
            "total_papers": total_papers,
            "total_topics": total_topics,
            "total_authors": total_authors,
            "total_gaps": total_gaps,
            "total_ideas": total_ideas
        },
        "topic_distribution": topic_distribution,
        "recent_papers": recent_list
    }

@router.get("/graph")
def get_knowledge_graph(
    current_user: User = Depends(get_current_user)
):
    """Fetches nodes and relations from active Graph database (Neo4j or local NetworkX)."""
    graph = get_graph_service()
    return graph.get_subgraph()
