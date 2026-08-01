# Smart India Hackathon (SIH) & Startup Pitch Deck Outline

**Project Title**: ResearchMind AI  
**Subtitle**: AI-Powered Scientific Research Gap Identifier using LLMs, RAG and Knowledge Graphs  
**Target Category**: EdTech / Research & Development Automation

---

## Slide 1: Title Slide
- **Project Name**: ResearchMind AI
- **Tagline**: Automatically parse, compare, and identify novel research gaps across thousands of scientific papers.
- **Presenter Names & Roles**: (e.g. Lead AI Engineer, Frontend developer, database architect).

---

## Slide 2: The Problem Statement
- **The Bottleneck**: Researchers, final-year students, and R&D labs spend **3 to 6 months** reading hundreds of academic papers before identifying a novel research gap or starting implementation.
- **Pain Points**:
  - **Information Overload**: Over 2 million scientific papers are published annually.
  - **No Methodological Maps**: Standard search engines (Google Scholar, IEEE Xplore) return list rankings, not side-by-side methodology/dataset comparison matrices.
  - **Hallucination Risk**: Standard chatbots (ChatGPT, Claude) lack persistent vector index mapping to fact-check source passages in PDFs.

---

## Slide 3: The Solution
- **ResearchMind AI**: A dual RAG-KG AI-powered scientific dashboard.
  - **Upload & Segment**: Parses PDF documents into sections (Abstract, Methodology, Limitations).
  - **Entity Linker (NER)**: Automatically extracts datasets, models, metrics, and hardware.
  - **Knowledge Graph Visualizer**: Renders interactive D3 topology maps linking authors, algorithms, and gaps.
  - **Research Gap Engine**: Automatically compares matrix intersections to compute an **Innovation Score**.
  - **Idea Generator**: Automatically proposes IEEE drafts, patent ideas, and startup MVPs.

---

## Slide 4: Technology Stack
- **Backend Services**: FastAPI, Python, SQLAlchemy, SQLite/PostgreSQL, Redis.
- **Frontend Panel**: React, TypeScript, TailwindCSS, D3.js (custom SVG force simulations), Recharts.
- **AI Pipelines**: Sentence Transformers (`all-MiniLM-L6-v2`), FAISS Vector Indexing, Ollama REST models (`qwen2:7b`, `gemma:2b`).
- **Graph Databases**: Neo4j Community Server & NetworkX fallback.

---

## Slide 5: The Innovation Core (How it Works)
- **High-Dimensional Vector Spaces**: Paper chunks are embedded and queried using cosine similarity.
- **Structural Relation Linking**: Entities (Datasets, Algorithms) are merged in the graph database.
- **The Gap Spotting Heuristic**: Intersects existing methods to find missing configurations, then feeds summaries to an instruction-tuned LLM to score novelty and build roadmaps.

---

## Slide 6: Product Demonstration / User Flow
1. **Upload**: Dropzone accepts batch PDF files (e.g. Lewis 2020, Gemma 2024).
2. **Dashboard**: Metrics update instantly; D3 Graph renders node links.
3. **Compare Matrix**: Checkbox selection compiles side-by-side parameters.
4. **Gap Analyzer**: Scan identifies limitations; LLM prints new project roadmaps.
5. **AI Chat**: Conversation logs display clickable context source pills.

---

## Slide 7: Market Potential & Commercialization
- **Target Audience**:
  - **Universities & Academics**: 40,000+ colleges in India (Final year projects, PhD research).
  - **Corporate R&D**: Pharma, AI labs, tech startups looking for competitor patent/paper overlays.
  - **Hackathons (SIH)**: Auto-generating and validating hackathon novel ideas.
- **Business Model**: SaaS subscription for universities (B2B) and individual premium credits for scholars (B2C).

---

## Slide 8: Development Roadmap
- **Phase 1 (MVP)**: Standalone SQLite + local vector indexing & NetworkX graph layout (Completed).
- **Phase 2 (Scalability)**: Docker containerization with PostgreSQL, Redis worker queues, and Neo4j servers (Completed).
- **Phase 3 (Production)**: Integration with online paper crawlers (arXiv, IEEE APIs) and multi-agent RAG reviews.

---

## Slide 9: Conclusion / Q&A
- **Summary**: ResearchMind AI turns months of tedious reading into seconds of structured, actionable research opportunities.
- **Contact Details**: (e.g., info@researchmind.ai)
- **Open for Q&A**
