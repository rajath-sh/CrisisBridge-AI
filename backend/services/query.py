"""
Query Service for CrisisBridge AI
===================================
The bridge between the API and the AI Core.
Handles:
- Cache lookups
- AI processing orchestration
- Database logging
- Session history updates
"""

import time
from typing import Optional
from sqlalchemy.orm import Session
from redis import Redis
from loguru import logger

from shared.schemas import (
    QueryRequest, QueryResponse, AIProcessRequest, AIProcessResponse
)
from shared.models import QueryLog, User
from shared.enums import CacheStatus
from backend.services.cache import CacheService
from ai_core.main import process_query


async def handle_query(
    db: Session,
    redis: Redis,
    request: QueryRequest,
    current_user: Optional[User] = None
) -> QueryResponse:
    """
    Main orchestration logic for a user query.
    1. Check cache
    2. If miss -> Call AI Core
    3. Log to DB
    4. Update session memory
    5. Return response
    """
    start_time = time.time()
    cache_service = CacheService(redis)
    
    # 1. ── Check Cache ──────────────────────────────────
    cached_data = cache_service.get_cached_response(request.query)
    
    if cached_data:
        response_time = (time.time() - start_time) * 1000
        
        # Construct response from cache
        ai_resp = AIProcessResponse(**cached_data)
        
        # Log the cached hit (optional, but good for analytics)
        query_log = _log_query(
            db, request, ai_resp, 
            CacheStatus.HIT, response_time, 
            current_user
        )
        
        return QueryResponse(
            answer=ai_resp.answer,
            sources=ai_resp.sources,
            confidence=ai_resp.confidence,
            explanation=ai_resp.explanation,
            cache_status=CacheStatus.HIT,
            response_time_ms=response_time,
            session_id=request.session_id,
            query_log_id=query_log.id
        )

    # 2. ── Cache Miss -> Process with AI Core ──────────
    
    # Get session history for context
    history = []
    if request.session_id:
        history = cache_service.get_session_history(request.session_id)
        
    ai_request = AIProcessRequest(
        query=request.query,
        session_id=request.session_id,
        session_history=history,
        category=request.category
    )
    
    try:
        ai_resp = await process_query(ai_request)
    except Exception as e:
        logger.error(f"AI Core processing failed: {e}")
        # Fallback response
        ai_resp = AIProcessResponse(
            answer="I'm sorry, I'm having trouble processing your request right now. Please try again or contact staff.",
            confidence=0.0,
            explanation=f"Error: {str(e)}"
        )

    response_time = (time.time() - start_time) * 1000

    # 3. ── Log to Database ──────────────────────────────
    query_log = _log_query(
        db, request, ai_resp, 
        CacheStatus.MISS, response_time, 
        current_user
    )

    # 4. ── Update Cache & Session ───────────────────────
    if ai_resp.confidence > 0.5: # Only cache if reasonably confident
        cache_service.set_cached_response(request.query, ai_resp)
        
    if request.session_id:
        cache_service.add_to_session_history(
            request.session_id, 
            request.query, 
            ai_resp.answer
        )

    # 5. ── Return Response ──────────────────────────────
    return QueryResponse(
        answer=ai_resp.answer,
        sources=ai_resp.sources,
        confidence=ai_resp.confidence,
        explanation=ai_resp.explanation,
        cache_status=CacheStatus.MISS,
        response_time_ms=response_time,
        session_id=request.session_id,
        query_log_id=query_log.id
    )


def _log_query(
    db: Session,
    request: QueryRequest,
    ai_resp: AIProcessResponse,
    cache_status: CacheStatus,
    response_time: float,
    user: Optional[User] = None
) -> QueryLog:
    """Internal helper to save query to PostgreSQL."""
    query_log = QueryLog(
        user_id=user.id if user else None,
        session_id=request.session_id,
        original_query=request.query,
        rewritten_query=ai_resp.rewritten_query,
        answer=ai_resp.answer,
        sources=ai_resp.sources,
        confidence=ai_resp.confidence,
        explanation=ai_resp.explanation,
        cache_status=cache_status,
        response_time_ms=response_time
    )
    
    try:
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        return query_log
    except Exception as e:
        logger.error(f"Database logging failed: {e}")
        db.rollback()
        # Return a dummy log object with id=None so the API doesn't crash
        return QueryLog(id=None)
