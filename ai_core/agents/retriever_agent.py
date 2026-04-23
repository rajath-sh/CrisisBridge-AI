from typing import List, Dict, Any
from ai_core.agents.base_agent import BaseAgent
from ai_core.rag.embeddings import EmbeddingModel
from ai_core.rag.vector_store import FAISSVectorStore
from ai_core.config import ai_config
import logging

logger = logging.getLogger(__name__)

class RetrieverAgent(BaseAgent):
    """
    Uses the rewritten query to fetch relevant document chunks from the FAISS vector store.
    """

    def __init__(self):
        super().__init__()
        self.embedder = EmbeddingModel()
        self.vector_store = FAISSVectorStore()

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Searches FAISS and returns a formatted context string and source metadata.
        """
        if ai_config.MOCK_MODE:
            return self._get_mock_response()

        # 1. Embed the query
        query_embedding = self.embedder.embed_query(query)
        
        # 2. Search FAISS
        results = self.vector_store.search(query_embedding, top_k=ai_config.TOP_K_RESULTS)
        
        if not results:
            logger.warning("No context found in vector store.")
            return {"context": "", "sources": []}

        # 3. Format the context for the LLM
        context_parts = []
        sources = []
        
        for dist, chunk in results:
            source_name = chunk['metadata'].get('source', 'Unknown')
            content = chunk['content']
            
            context_parts.append(f"--- SOURCE: {source_name} ---\n{content}\n")
            
            if source_name not in sources:
                sources.append(source_name)

        return {
            "context": "\n".join(context_parts),
            "sources": sources
        }

    def _get_mock_response(self) -> Dict[str, Any]:
        return {
            "context": "--- SOURCE: mock_fire_safety.txt ---\nIn case of fire, use the stairs and proceed to the assembly point.",
            "sources": ["mock_fire_safety.txt"]
        }
