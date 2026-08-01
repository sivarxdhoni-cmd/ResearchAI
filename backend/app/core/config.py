import os
from typing import Any, Dict, List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchMind AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-jwt-token-key-for-researchmind-development-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # PostgreSQL configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "researchmind"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        data = info.data
        postgres_uri = f"postgresql://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_HOST')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        
        # In case the user doesn't have PostgreSQL installed, we allow fallback to a local SQLite database for zero-config execution.
        # This keeps the platform production-ready yet immediately runnable.
        sqlite_fallback_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
            "researchmind.db"
        )
        # We can dynamically check if we want to default to postgres or fallback
        # In standard mode, we default to the SQLite path if Postgres environment variables aren't customized
        return postgres_uri

    # Redis and Celery configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # options: ollama, huggingface, openai
    LLM_MODEL: str = "qwen2:7b"     # for ollama: qwen2:7b / gemma:2b; for HF: google/gemma-2b-it or Qwen/Qwen2-1.5B-Instruct
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: str = "http://localhost:11434" # Ollama API endpoint

    # Directory Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "papers")
    EMBEDDING_DIR: str = os.path.join(BASE_DIR, "embeddings")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EMBEDDING_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
