import time
from ai_core.config import ai_config
from ai_core.rag.document_loader import DocumentLoader
from ai_core.rag.chunker import DocumentChunker
from ai_core.rag.embeddings import EmbeddingModel
from ai_core.rag.vector_store import FAISSVectorStore

class RAGIngestor:
    """
    Orchestrates the entire ingestion pipeline:
    Load Documents -> Chunk -> Embed -> Store in FAISS
    """

    def __init__(self, data_dir: str = None, index_dir: str = None):
        self.data_dir = data_dir or ai_config.SAFETY_DOCS_PATH
        self.index_dir = index_dir or ai_config.FAISS_INDEX_PATH
        
        self.loader = DocumentLoader(self.data_dir)
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingModel()
        self.vector_store = FAISSVectorStore(self.index_dir)

    def run_ingestion(self) -> dict:
        """
        Runs the full pipeline. Rebuilds the index from scratch by default.
        """
        print(f"🚀 Starting RAG Ingestion Pipeline")
        start_time = time.time()
        
        # 1. Load
        print(f"Loading documents from {self.data_dir}...")
        documents = self.loader.load_all()
        if not documents:
            print("❌ No documents found to ingest.")
            return {"status": "error", "message": "No documents found."}
        print(f"✅ Loaded {len(documents)} documents.")
        
        # 2. Chunk
        print("Chunking documents...")
        chunks = self.chunker.chunk_documents(documents)
        print(f"✅ Created {len(chunks)} text chunks.")
        
        # 3. Embed
        print("Generating embeddings via Google Gemini API...")
        # To avoid hitting API rate limits immediately, we could batch this
        # For small datasets (< 100 chunks), doing it all at once is fine
        texts_to_embed = [chunk.content for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts_to_embed)
        print(f"✅ Generated embeddings shape: {embeddings.shape}")
        
        # 4. Store
        print("Storing in FAISS...")
        # Reset the store to avoid duplicates if re-running
        self.vector_store.index = None
        self.vector_store.chunks = []
        
        self.vector_store.add_embeddings(chunks, embeddings)
        self.vector_store.save()
        print(f"✅ Saved FAISS index to {self.index_dir}")
        
        end_time = time.time()
        print(f"🎉 Ingestion complete in {end_time - start_time:.2f} seconds!")
        
        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": len(chunks),
            "time_seconds": round(end_time - start_time, 2)
        }
