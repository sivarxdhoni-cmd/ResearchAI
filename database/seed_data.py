import sys
import os

# Adjust path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.db.models import User, Paper, Topic, Dataset, Algorithm, Author, ResearchGap, ResearchIdea
from knowledge_graph import get_graph_service
from rag.search import RAGEngine

def seed_db():
    print("Syncing database schema...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    # 1. Create Users
    print("Seeding Users...")
    users = [
        {"email": "admin@researchmind.ai", "name": "System Administrator", "role": "Admin", "pass": "admin123"},
        {"email": "scholar@researchmind.ai", "name": "Dr. Sarah Jenkins", "role": "Research Scholar", "pass": "scholar123"},
        {"email": "student@researchmind.ai", "name": "Alex Riviera", "role": "Student", "pass": "student123"}
    ]
    
    for u in users:
        db_u = db.query(User).filter(User.email == u["email"]).first()
        if not db_u:
            db_u = User(
                email=u["email"],
                full_name=u["name"],
                role=u["role"],
                hashed_password=get_password_hash(u["pass"]),
                is_active=True
            )
            db.add(db_u)
    db.commit()

    # 2. Create Topics
    print("Seeding Topics...")
    topics_data = [
        {"name": "Large Language Models", "category": "NLP"},
        {"name": "Retrieval-Augmented Generation", "category": "NLP"},
        {"name": "Quantum Neural Networks", "category": "Quantum Computing"}
    ]
    
    topic_map = {}
    for td in topics_data:
        topic = db.query(Topic).filter(Topic.name == td["name"]).first()
        if not topic:
            topic = Topic(name=td["name"], category=td["category"])
            db.add(topic)
            db.flush()
        topic_map[td["name"]] = topic
        
    db.commit()

    # 3. Create Papers
    print("Seeding Papers, Authors, Datasets...")
    papers_data = [
        {
            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            "authors": ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus"],
            "year": 2020,
            "abstract": "We construct Retrieval-Augmented Generation (RAG) models, combining pre-trained parametric memory with non-parametric memory. RAG achieves state-of-the-art results on Open QA datasets.",
            "methodology": "We combine a dense passage retriever (DPR) query encoder with a sequence-to-sequence generator (BART-large). We index Wikipedia passages to query during generation.",
            "datasets": ["SQuAD", "TriviaQA", "MS-MARCO"],
            "algorithms": ["DPR", "BART", "Dense Vector Search"],
            "metrics": ["Exact Match: 44.5%", "F1-Score: 56.8%"],
            "limitations": "Retrieving passages during token generation increases decoding latency. Dense indices require massive RAM storage.",
            "future_work": "Future scope includes integrating multi-hop retrieval and utilizing compressed vector databases.",
            "topic": "Retrieval-Augmented Generation"
        },
        {
            "title": "Gemma: Open Models for AI Research and Innovation",
            "authors": ["Thomas Mesnard", "Sarah Jenkins", "Dr. Sarah Jenkins"],
            "year": 2024,
            "abstract": "We introduce Gemma, a family of open weights text-to-text models. Gemma achieves state-of-the-art capabilities across text reasoning, coding, and mathematical analysis.",
            "methodology": "We train transformer decoders on a corpus of 6 trillion tokens. Optimization includes Rotary Position Embeddings (RoPE) and multi-query attention.",
            "datasets": ["C4", "Wikipedia", "CommonCrawl"],
            "algorithms": ["Gemma-7B", "Transformer Decoder", "AdamW"],
            "metrics": ["MMLU: 64.3%", "GSM8k: 46.4%"],
            "limitations": "Model size limits local execution on lightweight edge devices. Vulnerable to hallucination on niche medical queries.",
            "future_work": "Subsequent work will implement edge quantization and hybrid CPU/NPU execution frameworks.",
            "topic": "Large Language Models"
        }
    ]

    rag_engine = RAGEngine()
    graph = get_graph_service()
    # Clear index & graph first to write clean seeds
    rag_engine.indexer.clear()
    graph.clear_graph()

    for pd in papers_data:
        paper = db.query(Paper).filter(Paper.title == pd["title"]).first()
        if not paper:
            paper = Paper(
                title=pd["title"],
                authors_text=", ".join(pd["authors"]),
                abstract=pd["abstract"],
                methodology=pd["methodology"],
                limitations=pd["limitations"],
                future_work=pd["future_work"],
                dataset_names=", ".join(pd["datasets"]),
                algorithms_used=", ".join(pd["algorithms"]),
                accuracy_results=", ".join(pd["metrics"]),
                publication_year=pd["year"],
                conference_journal="ArXiv Preprints",
                status="completed"
            )
            db.add(paper)
            db.flush()
            
            # Map Topic
            t_obj = topic_map.get(pd["topic"])
            if t_obj and t_obj not in paper.topics:
                paper.topics.append(t_obj)

            # Map Datasets
            for ds_name in pd["datasets"]:
                ds_obj = db.query(Dataset).filter(Dataset.name == ds_name).first()
                if not ds_obj:
                    ds_obj = Dataset(name=ds_name, description=f"Standard benchmark dataset")
                    db.add(ds_obj)
                    db.flush()
                if ds_obj not in paper.datasets:
                    paper.datasets.append(ds_obj)

            # Map Algorithms
            for al_name in pd["algorithms"]:
                al_obj = db.query(Algorithm).filter(Algorithm.name == al_name).first()
                if not al_obj:
                    al_obj = Algorithm(name=al_name, description=f"Model or architecture name")
                    db.add(al_obj)
                    db.flush()
                if al_obj not in paper.algorithms:
                    paper.algorithms.append(al_obj)

            # Map Authors
            for au_name in pd["authors"]:
                au_obj = db.query(Author).filter(Author.name == au_name).first()
                if not au_obj:
                    au_obj = Author(name=au_name)
                    db.add(au_obj)
                    db.flush()
                if au_obj not in paper.authors:
                    paper.authors.append(au_obj)

            db.commit()

            # Index chunks in RAG Vector DB
            chunks = [pd["abstract"], pd["methodology"], pd["limitations"], pd["future_work"]]
            sections = ["Abstract", "Methodology", "Limitations", "Future Scope"]
            rag_engine.add_paper_chunks(paper.id, paper.title, chunks, sections)

            # Connect in Graph Database
            graph.add_paper(paper.id, paper.title, paper.publication_year)
            for a in paper.authors:
                graph.add_author(a.name)
                graph.connect_author_paper(a.name, paper.id)
            for t in paper.topics:
                graph.add_topic(t.name, t.category)
                graph.connect_paper_topic(paper.id, t.name)
            for d in paper.datasets:
                graph.add_dataset(d.name)
                graph.connect_paper_dataset(paper.id, d.name)
            for al in paper.algorithms:
                graph.add_algorithm(al.name)
                graph.connect_paper_algorithm(paper.id, al.name)

    # 4. Seed a Research Gap & Research Idea
    print("Seeding Research Gap & Ideas...")
    rag_topic = topic_map["Retrieval-Augmented Generation"]
    gap = ResearchGap(
        topic_id=rag_topic.id,
        description="RAG systems suffer from high inference latency during token-by-token retrieval and lack optimized edge TPU compilation.",
        missing_methodology="Asynchronous speculative retrieval models",
        missing_dataset="CoLA / MultiQA",
        missing_hardware="Edge Coral TPU devices",
        missing_model="BART-mini / TinyLlama-1.1B",
        innovation_score=84.5
    )
    db.add(gap)
    db.flush()

    idea1 = ResearchIdea(
        gap_id=gap.id,
        title="Edge-RAG: Speculative Passage Retrieval Compiled for Edge TPUs",
        description="We propose a speculative retrieval architecture where a tiny local model predicts whether retrieval is necessary, compiling retrieval indexes on Edge Coral TPU USB accelerators for offline high-speed RAG.",
        type="IEEE",
        target_audience="Academic & Embedded Systems Researchers",
        novelty_score=89.0,
        roadmap_steps=[
            {"phase": "1. Quantization", "details": "Quantize embedding database to int8"},
            {"phase": "2. TPU Compile", "details": "Compile passage scoring metrics to TPU operators"},
            {"phase": "3. Speculation", "details": "Deploy confidence classifier to bypass unnecessary calls"}
        ]
    )
    idea2 = ResearchIdea(
        gap_id=gap.id,
        title="Offline Assistant for Disaster Relief Operations using Edge-RAG",
        description="A physical rugged device pre-loaded with local Wikipedia embeddings, running search locally on a Raspberry Pi + TPU without internet during disaster response.",
        type="SIH",
        target_audience="SIH Hackathon Hardware Edition",
        novelty_score=92.5,
        roadmap_steps=[
            {"phase": "1. Enclosure Build", "details": "3D print rugged casing with battery pack"},
            {"phase": "2. Database Seed", "details": "Pre-load medical & survival wiki passage vectors"},
            {"phase": "3. UI Setup", "details": "Create simple offline WiFi portal access point"}
        ]
    )
    db.add(idea1)
    db.add(idea2)
    db.commit()

    # Seed Graph nodes for gaps
    graph.add_research_gap(gap.id, gap.description, gap.innovation_score)
    graph.connect_gap_topic(gap.id, rag_topic.name)
    # Link all RAG papers to this gap
    rag_papers = db.query(Paper).join(Paper.topics).filter(Topic.id == rag_topic.id).all()
    for rp in rag_papers:
        graph.connect_paper_gap(rp.id, gap.id)

    print("\nDatabase seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_db()
