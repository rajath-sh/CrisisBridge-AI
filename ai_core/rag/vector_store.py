import os
import json
import faiss
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from ai_core.config import ai_config
from ai_core.rag.chunker import Chunk

class FAISSVectorStore:
    """
    Manages the FAISS index and associated chunk metadata.
    Handles saving to and loading from disk.
    """

    def __init__(self, index_dir: str = None):
        self.index_dir = Path(index_dir or ai_config.FAISS_INDEX_PATH)
        self.dimension = ai_config.EMBEDDING_DIMENSION
        
        # Internal state
        self.index = None
        self.chunks: List[dict] = []  # Stores the actual text and metadata
        
        # Load existing if available
        self._load_index()

    def add_embeddings(self, chunks: List[Chunk], embeddings: np.ndarray):
        """
        Adds new chunks and their embeddings to the store.
        """
        if len(chunks) == 0:
            return
            
        if len(chunks) != embeddings.shape[0]:
            raise ValueError(f"Mismatch: {len(chunks)} chunks, {embeddings.shape[0]} embeddings")

        # Initialize index if it doesn't exist
        if self.index is None:
            # Using L2 distance index (IndexFlatL2)
            self.index = faiss.IndexFlatL2(self.dimension)

        # Add vectors to FAISS
        self.index.add(embeddings)
        
        # Add metadata to our internal list
        for chunk in chunks:
            self.chunks.append({
                "content": chunk.content,
                "metadata": chunk.metadata
            })

    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Tuple[float, dict]]:
        """
        Searches the index for the closest vectors to the query_embedding.
        Returns a list of (distance, chunk_dict).
        """
        if self.index is None or self.index.ntotal == 0:
            return []
            
        if top_k is None:
            top_k = ai_config.TOP_K_RESULTS
            
        # FAISS expects 2D array, so reshape query if it's 1D
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Ensure query is float32
        query_embedding = query_embedding.astype(np.float32)

        # Search FAISS (returns distances and indices)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                # Distance: lower is better for L2
                dist = float(distances[0][i])
                chunk_data = self.chunks[idx]
                results.append((dist, chunk_data))
                
        return results

    def save(self):
        """Saves the FAISS index and chunk metadata to disk."""
        if self.index is None:
            return
            
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_dir / "index.faiss"))
        
        # Save metadata and text as JSON
        with open(self.index_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    def _load_index(self):
        """Loads the index and metadata if they exist."""
        index_file = self.index_dir / "index.faiss"
        chunks_file = self.index_dir / "chunks.json"
        
        if index_file.exists() and chunks_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load FAISS index: {e}")
                self.index = None
                self.chunks = []
