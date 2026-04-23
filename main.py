"""
CrisisBridge AI — Main Application Entry Point
=================================================
This is the SINGLE FastAPI app that everyone's routes plug into.

Person 3 owns this file, but the structure is set up so
Person 1 and Person 2 just add their routers — no merge conflicts.

Run:
    uvicorn main:app --reload --port 8000

All routes are prefixed with /api/v1/
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from shared.config import settings
from shared.database import init_db


# ── Logging setup ────────────────────────────────
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL, colorize=True)
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
)


# ── Lifespan (startup/shutdown) ──────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting CrisisBridge AI...")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
    
    # TODO: Person 3 — Initialize Redis connection check here
    # TODO: Person 2 — Load FAISS index here
    
    logger.info("✅ CrisisBridge AI is ready!")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CrisisBridge AI...")


# ── Create FastAPI app ───────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Emergency Coordination Platform for Hotels & Resorts",
    lifespan=lifespan,
)


# ── CORS Middleware ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════
# ROUTER REGISTRATION
# Each person adds their router below.
# Pattern: from <module>.routes import router as <name>_router
# ═══════════════════════════════════════════════════════════

# ── Person 1: Incident & Safety Routes ──────────
# Uncomment when Person 1's routes are ready:
# from incidents.routes import router as incidents_router
# app.include_router(incidents_router, prefix=f"{settings.API_PREFIX}/incidents", tags=["Incidents"])
# from incidents.safety_routes import router as safety_router
# app.include_router(safety_router, prefix=f"{settings.API_PREFIX}/safety", tags=["Safety"])

# ── Person 2: AI Query Routes ───────────────────
# Uncomment when Person 2's routes are ready:
# from ai_core.routes import router as ai_router
# app.include_router(ai_router, prefix=f"{settings.API_PREFIX}/ai", tags=["AI Assistant"])

# ── Person 3: Auth, Feedback, Notifications ─────
# Each person's routers are registered as they are implemented.
from backend.api.auth import router as auth_router
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])

# Placeholder for future Person 3 routes:
# from backend.api.feedback import router as feedback_router
# app.include_router(feedback_router, prefix=f"{settings.API_PREFIX}/feedback", tags=["Feedback"])
from backend.api.feedback import router as feedback_router
app.include_router(feedback_router, prefix=f"{settings.API_PREFIX}/feedback", tags=["Feedback"])

from backend.api.notifications import router as notifications_router
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])

from backend.api.query import router as query_router
app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query", tags=["Query"])

from backend.api.users import router as users_router
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK (Available immediately — no auth required)
# ═══════════════════════════════════════════════════════════

@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — redirects to docs."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }
