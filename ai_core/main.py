"""
AI Core — Clean Interface for Person 3
========================================
Person 3 calls ONLY this function. Never imports agents/rag directly.

Usage by Person 3:
    from ai_core.main import process_query
    result = await process_query(request)
"""

from shared.schemas import AIProcessRequest, AIProcessResponse
import logging

logger = logging.getLogger(__name__)

# We use a singleton instance so we don't recreate the FAISS index
# and Gemini clients on every single request.
_pipeline = None

async def process_query(request: AIProcessRequest) -> AIProcessResponse:
    """
    Main entry point for AI processing.
    
    Person 2 implemented the full pipeline behind this function:
    1. Query Rewriting Agent
    2. Retriever Agent (FAISS search)
    3. Reasoning Agent
    4. Validator Agent  
    5. Explainer Agent
    
    Person 3 calls this function from the /query API endpoint.
    
    Args:
        request: AIProcessRequest with query, session info, history
        
    Returns:
        AIProcessResponse with answer, sources, confidence, explanation
    """
    global _pipeline
    
    # Lazy load the pipeline to prevent circular imports and allow fast startup
    if _pipeline is None:
        from ai_core.pipeline import MultiAgentPipeline
        _pipeline = MultiAgentPipeline()
        
    try:
        return await _pipeline.process(request)
    except Exception as e:
        logger.error(f"Top-level AI error: {e}", exc_info=True)
        return AIProcessResponse(
            answer="I'm sorry, I encountered a critical error. Please dial 0 for the front desk immediately.",
            sources=[],
            confidence=0.0,
            explanation=f"Error: {str(e)}",
            agent_trace=[]
        )
