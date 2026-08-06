import sys
import os

# Adjust path to import local modules when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base
from backend.app.api import auth, papers, chat, gaps, dashboard

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("researchmind")

# Create database tables automatically on startup
logger.info("Initializing relational database tables...")
Base.metadata.create_all(bind=engine)

# Auto-seed database if empty
try:
    from backend.app.db.session import SessionLocal
    from backend.app.db.models import User
    db = SessionLocal()
    if db.query(User).count() == 0:
        logger.info("Database is empty. Running auto-seeding...")
        from database.seed_data import seed_db
        seed_db()
    db.close()
except Exception as e:
    logger.error(f"Failed to auto-seed database: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sivarxdhoni-cmd.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(papers.router, prefix=f"{settings.API_V1_STR}/papers", tags=["Papers"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["AI Chat Assistant"])
app.include_router(gaps.router, prefix=f"{settings.API_V1_STR}/gaps", tags=["Research Gap Engine"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "api_version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("backend.run:app", host="0.0.0.0", port=8000, reload=True)
