# ResearchMind AI: Scientific Research Gap Identifier Platform

**Live Website:** [https://sivarxdhoni-cmd.github.io/ResearchAI/](https://sivarxdhoni-cmd.github.io/ResearchAI/)

ResearchMind AI is an enterprise-grade AI assistant designed to accelerate literature reviews, map scientific citation relations, detect methodology overlaps, compute Innovation Scores, and draft publication proposals.

Designed for Final Year Projects, Smart India Hackathon (SIH) demonstrations, IEEE publications, and Startup MVPs.

---

## Technical Architecture Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery (task worker).
- **Frontend**: React, TypeScript, TailwindCSS (v3), D3.js (knowledge graph network).
- **AI & RAG Engine**: Sentence Transformers, FAISS Vector Indexing, customizable LLM Provider interface (Ollama REST / HuggingFace Pipelines / OpenAI API).
- **Knowledge Graph**: Neo4j (via Cypher driver) with local NetworkX serialization fallback.

---

## Directory Structure

```
researchmind/
├── backend/            # FastAPI REST backend & services
│   ├── app/
│   │   ├── api/        # Routers (auth, papers, chat, gaps, dashboard)
│   │   ├── core/       # Security, JWT tokens, configurations
│   │   ├── db/         # SQLAlchemy models & sessions
│   │   ├── schemas/    # Pydantic schema validation
│   │   └── services/   # Paper processors & worker tasks
│   └── run.py          # FastAPI server entry point
├── frontend/           # React TypeScript (Vite) SPA client
├── ai/                 # Text extractor (fitz) & NER pipelines
├── rag/                # Vector store adapters (FAISS / Local JSON)
├── knowledge_graph/    # Graph database client (Neo4j / NetworkX JSON)
├── database/           # DB schema creations and seeding
├── deployment/         # Dockerfiles and Compose orchestration
├── reports/            # Project pitch and IEEE reports
└── tests/              # Backend endpoint verification suite
```

---

## Local Quick Start (Zero-Config / Standalone)

To run the application immediately without installing external database servers (PostgreSQL/Neo4j) or GPU vector backends, the codebase uses **automatic local fallbacks** (SQLite, local NetworkX graphs, and character-hashing mock vector indices).

### 1. Backend Setup
1. Open terminal and navigate to the project directory:
   ```bash
   cd researchmind
   ```
2. Install dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```
3. Initialize and seed database records:
   ```bash
   py database/seed_data.py
   ```
4. Run the FastAPI development server:
   ```bash
   py backend/run.py
   ```
   *The API will listen at `http://localhost:8000`. Access `http://localhost:8000/docs` to open Swagger UI.*

### 2. Frontend Setup
1. In a separate terminal, navigate to the frontend folder:
   ```bash
   cd researchmind/frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite hot-reloading dev server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

---

## Enterprise Production Startup (Docker Compose)

To spin up all services (FastAPI, React, PostgreSQL, Redis, Celery, and Neo4j) simultaneously inside Docker:

1. Navigate to the deployment folder:
   ```bash
   cd researchmind/deployment
   ```
2. Launch containers:
   ```bash
   docker-compose up --build -d
   ```
3. Access services:
   - **Frontend UI**: `http://localhost`
   - **FastAPI API Docs**: `http://localhost:8000/docs`
   - **Neo4j Dashboard**: `http://localhost:7474` (Credentials: `neo4j` / `password123`)

---

## LLM Configurations & Integrations

In `backend/app/core/config.py`, customize your active LLM Provider:

### Ollama (Recommended Local Option)
Ensure Ollama is running (`ollama serve`) and pull the target model (e.g. `ollama pull qwen2:7b` or `gemma:2b`).
```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2:7b
LLM_BASE_URL=http://localhost:11434
```

### HuggingFace (Direct Python Execution)
The server will download model weights and run inference inside the Python process (requires PyTorch & Transformers).
```env
LLM_PROVIDER=huggingface
LLM_MODEL=google/gemma-2b-it
```

### OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
LLM_API_KEY=your-openai-api-key-here
```
