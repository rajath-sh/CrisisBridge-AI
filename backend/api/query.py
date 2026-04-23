"""
Query API Routes for CrisisBridge AI
=====================================
Endpoints:
- POST /query
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
from typing import Optional

from shared.dependencies import get_db, get_redis, get_current_user_optional
from shared.schemas import QueryRequest, QueryResponse
from shared.models import User
from backend.services import query as query_service

router = APIRouter()


@router.post(
    "", 
    response_model=QueryResponse,
    summary="Ask a question to the AI Crisis Assistant"
)
async def query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Main query endpoint for the AI Assistant.
    
    - Checks Redis cache first for fast response.
    - Uses session_id to maintain conversational context.
    - If no cache, triggers the Multi-Agent RAG pipeline (ai_core).
    - Logs results for analytics and feedback.
    """
    return await query_service.handle_query(
        db=db,
        redis=redis,
        request=request,
        current_user=current_user
    )
