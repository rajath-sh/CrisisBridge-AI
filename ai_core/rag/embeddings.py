import numpy as np
from typing import List, Union
from google import genai
from ai_core.config import ai_config


class EmbeddingModel:
    """
    Wrapper for Google's Gemini Text Embedding model.
    Uses the new google-genai SDK.
    """

    def __init__(self):
        self._client = None
        self.model_name = ai_config.EMBEDDING_MODEL

    @property
    def client(self) -> genai.Client:
        """Lazy load the Gemini client."""
        if self._client is None and not ai_config.MOCK_MODE:
            if ai_config.USE_VERTEX_AI:
                self._client = genai.Client(
                    vertexai=True,
                    project=ai_config.GCP_PROJECT_ID,
                    location=ai_config.GCP_LOCATION
                )
            else:
                self._client = genai.Client(api_key=ai_config.GEMINI_API_KEY)
        return self._client

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of strings and returns a numpy array of shape (N, dim).
        Handles Google API's 100-item batch limit automatically.
        """
        if not texts:
            return np.empty((0, ai_config.EMBEDDING_DIMENSION), dtype=np.float32)

        try:
            from google.genai import types
            import time
            BATCH_SIZE = 90  # Stay under the 100/minute free tier limit
            all_embeddings = []
            
            # Process in batches to avoid API limit
            for i in range(0, len(texts), BATCH_SIZE):
                batch_texts = texts[i:i + BATCH_SIZE]
                
                contents_batch = [
                    types.Content(role='user', parts=[types.Part.from_text(text=t)]) 
                    for t in batch_texts
                ]
                
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=contents_batch
                )
                
                batch_embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(batch_embeddings)
                
                print(f"  ... embedded {len(all_embeddings)}/{len(texts)} chunks")
                
                # If there are more chunks to process, we must wait 60 seconds 
                # because the free tier allows only 100 embeddings per minute.
                if i + BATCH_SIZE < len(texts):
                    print("  ... ⏳ Waiting 60 seconds to respect Google's Free Tier limits (100 per min)...")
                    time.sleep(60)
            
            # Convert to float32 numpy array for FAISS
            return np.array(all_embeddings, dtype=np.float32)
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return empty array of correct shape on failure
            return np.empty((0, ai_config.EMBEDDING_DIMENSION), dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string and returns a 1D numpy array.
        """
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=query
            )
            embedding = response.embeddings[0].values
            return np.array(embedding, dtype=np.float32)
            
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return np.zeros(ai_config.EMBEDDING_DIMENSION, dtype=np.float32)
