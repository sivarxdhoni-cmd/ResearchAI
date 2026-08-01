import logging
from typing import Dict, Any, List, Tuple
from ai.models import get_llm_provider, EmbeddingService
from rag.indexer import VectorStoreIndexer

logger = logging.getLogger("researchmind")

class RAGEngine:
    def __init__(self):
        # We initialize local embedding generator and vector indexer
        # Using "local" for embedding provider (or "ollama" depending on setup)
        from backend.app.core.config import settings
        self.embedding_service = EmbeddingService(
            provider=settings.LLM_PROVIDER,
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY
        )
        self.indexer = VectorStoreIndexer()

    def add_paper_chunks(self, paper_id: int, paper_title: str, text_chunks: List[str], section_names: List[str]) -> None:
        """Embeds and indexes chunks of a paper into the vector store."""
        if not text_chunks:
            return

        vectors = []
        metadata_list = []

        for i, (chunk, sec) in enumerate(zip(text_chunks, section_names)):
            # Generate embedding vector
            vec = self.embedding_service.get_embedding(chunk)
            vectors.append(vec)
            
            # Format metadata
            metadata_list.append({
                "paper_id": paper_id,
                "title": paper_title,
                "section": sec,
                "text": chunk,
                "chunk_index": i
            })

        self.indexer.add_vectors(vectors, metadata_list)
        logger.info(f"Indexed {len(text_chunks)} chunks for paper ID: {paper_id}")

    def query(self, query_text: str, top_k: int = 4) -> Dict[str, Any]:
        """Runs the RAG flow: embeds the query, searches vectors, compiles prompt, and invokes the LLM."""
        # 1. Embed query
        query_vec = self.embedding_service.get_embedding(query_text)

        # 2. Search index
        matches = self.indexer.search(query_vec, k=top_k)
        if not matches:
            return {
                "answer": "I couldn't find any relevant details in the uploaded paper database to answer your question.",
                "sources": []
            }

        # 3. Format context
        context_blocks = []
        sources = []
        seen_chunks = set()

        for meta, score in matches:
            chunk_id = f"{meta['paper_id']}_{meta['chunk_index']}"
            if chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk_id)
            
            context_blocks.append(
                f"Source Document: {meta['title']}\n"
                f"Section: {meta['section']}\n"
                f"Content: {meta['text']}\n"
                f"---"
            )
            sources.append({
                "paper_id": meta["paper_id"],
                "title": meta["title"],
                "section": meta["section"],
                "text": meta["text"][:300] + "..." if len(meta["text"]) > 300 else meta["text"],
                "relevance_score": round(score, 3)
            })

        context_str = "\n\n".join(context_blocks)

        # 4. Invoke LLM with System prompt guiding structured answers
        system_prompt = (
            "You are a helpful and expert AI Scientific Research Assistant. Your task is to answer "
            "the user's questions based on the provided scientific literature contexts. "
            "Adhere to these rules:\n"
            "1. Only use the provided context to answer. If the context doesn't contain the answer, say so.\n"
            "2. Cite your sources in the text using [Source Document Title].\n"
            "3. Be objective, precise, and professional. Synthesize methodologies, datasets, and algorithms where applicable."
        )

        prompt = (
            f"Context from uploaded scientific papers:\n"
            f"========================================\n"
            f"{context_str}\n"
            f"========================================\n\n"
            f"User Question: {query_text}\n\n"
            f"Provide a clear, detailed response including citation markers:"
        )

        try:
            llm = get_llm_provider()
            answer = llm.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"LLM RAG execution failed: {e}")
            answer = (
                f"[System Error] LLM generation failed. I found the following relevant matches:\n"
                + "\n".join(f"- {s['title']} ({s['section']})" for s in sources)
            )

        return {
            "answer": answer,
            "sources": sources
        }
