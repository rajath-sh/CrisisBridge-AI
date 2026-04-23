"""
Cache Service for CrisisBridge AI
===================================
Handles:
- AI Response caching (Redis)
- Session memory management
- Key generation for cache
"""

import json
from typing import Optional, List, Dict, Any
from redis import Redis
from loguru import logger

from shared.config import settings
from shared.enums import CacheStatus
from shared.schemas import AIProcessResponse


class CacheService:
    """
    Handles all Redis-based caching and session memory.
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = settings.CACHE_TTL_SECONDS
        self.session_limit = settings.SESSION_MEMORY_SIZE

    # ── AI Query Caching ─────────────────────────────

    def _get_query_key(self, query: str) -> str:
        """Generates a normalized cache key for a query."""
        # Simple normalization: lowercase and strip
        normalized = query.lower().strip()
        return f"cache:query:{normalized}"

    def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a cached AI response if it exists.
        Returns the raw dict or None.
        """
        key = self._get_query_key(query)
        try:
            cached = self.redis.get(key)
            if cached:
                logger.debug(f"Cache HIT for query: {query[:50]}...")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
        
        return None

    def set_cached_response(self, query: str, response: AIProcessResponse):
        """
        Stores an AI response in cache.
        """
        key = self._get_query_key(query)
        try:
            # We store the dict representation of the response
            data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
            self.redis.setex(
                key,
                self.ttl,
                json.dumps(data)
            )
            logger.debug(f"Cache SET for query: {query[:50]}...")
        except Exception as e:
            logger.error(f"Redis set failed: {e}")

    # ── Session Memory ───────────────────────────────

    def _get_session_key(self, session_id: str) -> str:
        """Key for storing session history."""
        return f"session:history:{session_id}"

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the last N query-answer pairs for a session.
        """
        if not session_id:
            return []
            
        key = self._get_session_key(session_id)
        try:
            history = self.redis.lrange(key, 0, self.session_limit - 1)
            return [json.loads(h) for h in history]
        except Exception as e:
            logger.error(f"Redis lrange failed: {e}")
            return []

    def add_to_session_history(self, session_id: str, query: str, answer: str):
        """
        Adds a new Q&A pair to the session history.
        Maintains only the last N items.
        """
        if not session_id:
            return
            
        key = self._get_session_key(session_id)
        data = {"query": query, "answer": answer}
        
        try:
            # Push to front of list
            self.redis.lpush(key, json.dumps(data))
            # Trim to limit
            self.redis.ltrim(key, 0, self.session_limit - 1)
            # Set expiry for session (e.g., 24 hours)
            self.redis.expire(key, 86400)
        except Exception as e:
            logger.error(f"Redis session update failed: {e}")
