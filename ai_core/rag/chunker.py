from typing import List
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ai_core.config import ai_config
from ai_core.rag.document_loader import Document

@dataclass
class Chunk:
    """A text chunk with metadata."""
    content: str
    metadata: dict
    chunk_index: int


class DocumentChunker:
    """
    Splits large documents into smaller chunks suitable for embedding
    and retrieval, while preserving metadata.
    """

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=ai_config.CHUNK_SIZE,
            chunk_overlap=ai_config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
            keep_separator=True
        )

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Takes a list of Documents and returns a flat list of Chunks.
        """
        all_chunks = []
        
        for doc in documents:
            # Split the text
            text_splits = self.splitter.split_text(doc.content)
            
            # Create Chunk objects with metadata
            for i, text in enumerate(text_splits):
                # Copy the original metadata and add chunk info
                chunk_meta = doc.metadata.copy()
                chunk_meta["chunk_index"] = i
                
                chunk = Chunk(
                    content=text.strip(),
                    metadata=chunk_meta,
                    chunk_index=i
                )
                all_chunks.append(chunk)
                
        return all_chunks
