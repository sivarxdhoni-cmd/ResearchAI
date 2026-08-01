import os
import json
import logging
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.app.core.config import settings

logger = logging.getLogger("researchmind")

class VectorStoreIndexer:
    def __init__(self):
        self.index_dir = settings.EMBEDDING_DIR
        self.index_path = os.path.join(self.index_dir, "faiss_index.bin")
        self.meta_path = os.path.join(self.index_dir, "metadata.json")
        self.dimension = 384  # Standard size for all-MiniLM-L6-v2
        
        self.faiss_index = None
        self.metadata: List[Dict[str, Any]] = []  # Index maps 1-to-1 to lines
        self.python_vectors: List[List[float]] = []  # Fallback vector store
        
        self._initialize()

    def _initialize(self):
        """Initializes FAISS or sets up the local Python vector store fallback."""
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Load metadata if it exists
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load vector metadata: {e}")
                self.metadata = []

        try:
            import faiss
            logger.info("Initializing FAISS vector store...")
            if os.path.exists(self.index_path):
                try:
                    self.faiss_index = faiss.read_index(self.index_path)
                    logger.info(f"Loaded existing FAISS index from: {self.index_path}")
                except Exception as e:
                    logger.warning(f"Failed to read existing FAISS binary ({e}). Creating new index.")
                    self.faiss_index = faiss.IndexFlatIP(self.dimension)  # Inner Product (Cosine similarity if normalized)
            else:
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
        except Exception as e:
            logger.warning(f"FAISS not available ({e}). Using pure-Python vector database fallback.")
            self.faiss_index = None
            
            # Load vectors for Python fallback if saved
            fallback_vec_path = os.path.join(self.index_dir, "fallback_vectors.json")
            if os.path.exists(fallback_vec_path):
                try:
                    with open(fallback_vec_path, "r", encoding="utf-8") as f:
                        self.python_vectors = json.load(f)
                    logger.info(f"Loaded {len(self.python_vectors)} fallback vectors from disk.")
                except Exception as ex:
                    logger.error(f"Failed to load fallback vectors: {ex}")
                    self.python_vectors = []

    def save(self):
        """Saves vectors and metadata to disk."""
        try:
            # Save metadata
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)

            if self.faiss_index is not None:
                import faiss
                faiss.write_index(self.faiss_index, self.index_path)
                logger.info(f"Persisted FAISS index to {self.index_path}")
            else:
                # Save python fallback vectors
                fallback_vec_path = os.path.join(self.index_dir, "fallback_vectors.json")
                with open(fallback_vec_path, "w", encoding="utf-8") as f:
                    json.dump(self.python_vectors, f)
                logger.info(f"Persisted local fallback vectors to {fallback_vec_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def add_vectors(self, vectors: List[List[float]], metadata_list: List[Dict[str, Any]]) -> List[int]:
        """Adds a list of embeddings and their matching metadata chunks to the database."""
        if not vectors or len(vectors) != len(metadata_list):
            return []

        ids = []
        start_idx = len(self.metadata)
        
        # Norm function to ensure cosine similarity matches inner product
        normalized_vectors = []
        for vec in vectors:
            arr = np.array(vec, dtype=np.float32)
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            normalized_vectors.append(arr)

        if self.faiss_index is not None:
            data_matrix = np.vstack(normalized_vectors).astype(np.float32)
            self.faiss_index.add(data_matrix)
            for i, meta in enumerate(metadata_list):
                idx = start_idx + i
                meta["vector_id"] = idx
                self.metadata.append(meta)
                ids.append(idx)
        else:
            for i, vec in enumerate(normalized_vectors):
                idx = start_idx + i
                self.python_vectors.append(vec.tolist())
                meta = metadata_list[i]
                meta["vector_id"] = idx
                self.metadata.append(meta)
                ids.append(idx)
                
        self.save()
        return ids

    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Searches vector database for nearest matches. Returns list of (metadata, score)."""
        if not self.metadata or not query_vector:
            return []

        # Normalize query vector
        q_arr = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 0:
            q_arr = q_arr / q_norm

        results = []

        if self.faiss_index is not None and self.faiss_index.ntotal > 0:
            try:
                import faiss
                # Query index
                q_matrix = q_arr.reshape(1, -1).astype(np.float32)
                scores, indices = self.faiss_index.search(q_matrix, k)
                
                for score, idx in zip(scores[0], indices[0]):
                    if idx < 0 or idx >= len(self.metadata):
                        continue
                    results.append((self.metadata[idx], float(score)))
            except Exception as e:
                logger.error(f"FAISS search failed: {e}. Falling back to matrix operations.")

        # Fallback Python matrix search if FAISS failed or is empty
        if not results and self.metadata:
            # Perform matrix dot product
            vecs = np.array(self.python_vectors, dtype=np.float32)
            # Dot products between normalized query vector and all normalized dataset vectors
            scores = np.dot(vecs, q_arr)
            
            # Sort indices descending
            top_k_indices = np.argsort(scores)[::-1][:k]
            for idx in top_k_indices:
                if idx < 0 or idx >= len(self.metadata):
                    continue
                results.append((self.metadata[idx], float(scores[idx])))
                
        return results

    def clear(self):
        """Clears all vectors and metadata."""
        self.metadata = []
        self.python_vectors = []
        if self.faiss_index is not None:
            self.faiss_index = None
            try:
                import faiss
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
            except ImportError:
                pass
        self.save()
