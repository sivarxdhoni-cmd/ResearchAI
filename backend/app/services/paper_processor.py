import os
import logging
from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.db.models import Paper, Topic, Dataset, Algorithm, Author, EmbeddingChunk
from ai.extractor import PDFExtractor
from ai.ner import NREngine
from rag.search import RAGEngine
from knowledge_graph import get_graph_service

logger = logging.getLogger("researchmind")

def split_text_into_chunks(text: str, chunk_size: int = 800, overlap: int = 150) -> list:
    """Splits a long block of text into overlapping semantic/character-based chunks."""
    if not text:
        return []
        
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Handle long paragraphs
            if len(para) > chunk_size:
                start = 0
                while start < len(para):
                    chunks.append(para[start:start+chunk_size])
                    start += chunk_size - overlap
                current_chunk = ""
            else:
                current_chunk = para + "\n\n"
                
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def process_paper_background(paper_id: int) -> None:
    """Core worker task that analyzes the uploaded PDF and populates the database, vectors, and graph."""
    db: Session = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            logger.error(f"Paper processor: Paper ID {paper_id} not found in database.")
            return

        logger.info(f"Background task starting for Paper: {paper.title or paper.pdf_path}")
        
        # 1. Parse PDF layout
        extractor = PDFExtractor()
        parsed_data = extractor.parse_structure(paper.pdf_path)
        
        # Update details in the database
        paper.title = parsed_data.get("title") or paper.title or "Untitled Paper"
        paper.authors_text = parsed_data.get("authors") or "Unknown"
        paper.abstract = parsed_data.get("abstract")
        paper.methodology = parsed_data.get("methodology")
        paper.limitations = parsed_data.get("limitations")
        paper.future_work = parsed_data.get("future_work")
        paper.conclusion = parsed_data.get("conclusion")
        
        # 2. Extract Entities (NER & Keyphrase)
        ner = NREngine()
        entities = ner.analyze_paper_metadata(parsed_data)
        
        # Set extracted entities text for easy viewing
        paper.dataset_names = ", ".join(entities["datasets"])
        paper.algorithms_used = ", ".join(entities["algorithms"])
        paper.accuracy_results = ", ".join(entities["metrics"])
        paper.keywords = ", ".join(entities["keywords"])
        
        # Link topics in Database
        for kw in entities["keywords"]:
            topic = db.query(Topic).filter(Topic.name == kw).first()
            if not topic:
                topic = Topic(name=kw, category="Auto-Extracted")
                db.add(topic)
                db.flush()
            if topic not in paper.topics:
                paper.topics.append(topic)
                
        # Link datasets in Database
        for ds in entities["datasets"]:
            dataset = db.query(Dataset).filter(Dataset.name == ds).first()
            if not dataset:
                dataset = Dataset(name=ds, description=f"Dataset extracted from '{paper.title}'")
                db.add(dataset)
                db.flush()
            if dataset not in paper.datasets:
                paper.datasets.append(dataset)

        # Link algorithms in Database
        for algo in entities["algorithms"]:
            algorithm = db.query(Algorithm).filter(Algorithm.name == algo).first()
            if not algorithm:
                algorithm = Algorithm(name=algo, description=f"Algorithm extracted from '{paper.title}'")
                db.add(algorithm)
                db.flush()
            if algorithm not in paper.algorithms:
                paper.algorithms.append(algorithm)

        # Link authors in Database
        authors_list = [a.strip() for a in paper.authors_text.split(",") if a.strip()]
        for auth_name in authors_list:
            if not auth_name or len(auth_name) > 100:
                continue
            author = db.query(Author).filter(Author.name == auth_name).first()
            if not author:
                author = Author(name=auth_name)
                db.add(author)
                db.flush()
            if author not in paper.authors:
                paper.authors.append(author)

        db.commit()

        # 3. Create Chunk Embeddings & Index in Vector DB
        rag_engine = RAGEngine()
        
        # Collect sections to chunk
        sections_to_index = [
            ("Abstract", paper.abstract),
            ("Methodology", paper.methodology),
            ("Results/Evaluation", parsed_data.get("results")),
            ("Limitations", paper.limitations),
            ("Future Scope", paper.future_work),
            ("Conclusion", paper.conclusion)
        ]
        
        all_chunks = []
        all_section_names = []
        
        for sec_name, sec_text in sections_to_index:
            if not sec_text:
                continue
            chunks = split_text_into_chunks(sec_text)
            all_chunks.extend(chunks)
            all_section_names.extend([sec_name] * len(chunks))
            
        # Add to FAISS Vector store
        rag_engine.add_paper_chunks(paper.id, paper.title, all_chunks, all_section_names)
        
        # Save chunks mapping back to SQL DB for citation lookup
        for idx, (chunk, sec) in enumerate(zip(all_chunks, all_section_names)):
            db_chunk = EmbeddingChunk(
                paper_id=paper.id,
                chunk_index=idx,
                text_content=chunk,
                vector_id=idx # Maps to index in FAISS vector store
            )
            db.add(db_chunk)
            
        # 4. Construct Relationships in the Knowledge Graph
        graph = get_graph_service()
        
        # Add nodes
        graph.add_paper(paper.id, paper.title, paper.publication_year or 2026)
        
        for author in paper.authors:
            graph.add_author(author.name)
            graph.connect_author_paper(author.name, paper.id)
            
        for topic in paper.topics:
            graph.add_topic(topic.name, topic.category)
            graph.connect_paper_topic(paper.id, topic.name)
            
        for dataset in paper.datasets:
            graph.add_dataset(dataset.name)
            graph.connect_paper_dataset(paper.id, dataset.name)
            
        for algorithm in paper.algorithms:
            graph.add_algorithm(algorithm.name)
            graph.connect_paper_algorithm(paper.id, algorithm.name)

        # Mark paper status as completed
        paper.status = "completed"
        db.commit()
        logger.info(f"Successfully processed and indexed Paper ID {paper_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to process paper ID {paper_id}: {e}", exc_info=True)
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                paper.status = "error"
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to write error status to paper {paper_id}: {db_err}")
    finally:
        db.close()
