import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Boolean, Float, Table, JSON
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

# Association Tables for Many-to-Many Relationships
paper_author = Table(
    "paper_author",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
)

paper_topic = Table(
    "paper_topic",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
)

paper_algorithm = Table(
    "paper_algorithm",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("algorithm_id", Integer, ForeignKey("algorithms.id", ondelete="CASCADE"), primary_key=True)
)

paper_dataset = Table(
    "paper_dataset",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("dataset_id", Integer, ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="Student")  # Student, Research Scholar, Professor, Research Lab, Admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True, nullable=False)
    abstract = Column(Text, nullable=True)
    authors_text = Column(Text, nullable=True)  # Comma-separated list for easy view
    keywords = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="processing")  # processing, completed, error
    pdf_path = Column(String(500), nullable=True)
    doi = Column(String(100), nullable=True)
    arxiv_url = Column(String(500), nullable=True)
    publication_year = Column(Integer, nullable=True)
    conference_journal = Column(String(500), nullable=True)

    # Extracted structured contents
    methodology = Column(Text, nullable=True)
    dataset_names = Column(Text, nullable=True)
    algorithms_used = Column(Text, nullable=True)
    accuracy_results = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    future_work = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)

    # Relationships
    authors = relationship("Author", secondary=paper_author, back_populates="papers")
    topics = relationship("Topic", secondary=paper_topic, back_populates="papers")
    algorithms = relationship("Algorithm", secondary=paper_algorithm, back_populates="papers")
    datasets = relationship("Dataset", secondary=paper_dataset, back_populates="papers")
    chunks = relationship("EmbeddingChunk", back_populates="paper", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    affiliation = Column(String(500), nullable=True)

    papers = relationship("Paper", secondary=paper_author, back_populates="authors")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    papers = relationship("Paper", secondary=paper_topic, back_populates="topics")
    gaps = relationship("ResearchGap", back_populates="topic", cascade="all, delete-orphan")

class Algorithm(Base):
    __tablename__ = "algorithms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    papers = relationship("Paper", secondary=paper_algorithm, back_populates="algorithms")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    size_info = Column(String(100), nullable=True)

    papers = relationship("Paper", secondary=paper_dataset, back_populates="datasets")

class EmbeddingChunk(Base):
    __tablename__ = "embedding_chunks"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    vector_id = Column(Integer, nullable=True)  # Maps to physical index in the FAISS vector DB

    paper = relationship("Paper", back_populates="chunks")

class ResearchGap(Base):
    __tablename__ = "research_gaps"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    missing_methodology = Column(Text, nullable=True)
    missing_dataset = Column(Text, nullable=True)
    missing_hardware = Column(Text, nullable=True)
    missing_model = Column(Text, nullable=True)
    innovation_score = Column(Float, default=0.0)  # 0.0 to 100.0
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)

    topic = relationship("Topic", back_populates="gaps")
    ideas = relationship("ResearchIdea", back_populates="gap", cascade="all, delete-orphan")

class ResearchIdea(Base):
    __tablename__ = "research_ideas"

    id = Column(Integer, primary_key=True, index=True)
    gap_id = Column(Integer, ForeignKey("research_gaps.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # IEEE, SIH, Patent, Startup
    target_audience = Column(String(255), nullable=True)
    roadmap_steps = Column(JSON, nullable=True)  # List of dict steps
    novelty_score = Column(Float, default=0.0)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    gap = relationship("ResearchGap", back_populates="ideas")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of source chunks and document IDs
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_histories")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # IEEE, SIH, PPT
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reports")
