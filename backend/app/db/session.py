import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger("researchmind")

# Create engine with fallback mechanism
try:
    # Try connecting to PostgreSQL
    # Set a short connect_timeout so we don't block forever if PostgreSQL is down
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    if db_uri.startswith("postgresql://"):
        engine = create_engine(
            db_uri,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3}
        )
        # Test connection
        with engine.connect() as conn:
            logger.info("Successfully connected to PostgreSQL database.")
    else:
        raise ValueError("Non-Postgres URI specified, falling back to SQLite.")
except Exception as e:
    logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
    import os
    sqlite_path = os.path.join(settings.BASE_DIR, "researchmind.db")
    db_uri = f"sqlite:///{sqlite_path}"
    engine = create_engine(
        db_uri,
        connect_args={"check_same_thread": False}
    )
    logger.info(f"Initialized SQLite database at: {sqlite_path}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
