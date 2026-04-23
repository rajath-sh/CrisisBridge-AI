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
from fastapi.staticfiles import StaticFiles
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
    logger.info("Starting CrisisBridge AI...")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    logger.info("CrisisBridge AI is ready!")
    yield
    
    # Shutdown
    logger.info("Shutting down CrisisBridge AI...")


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
# ═══════════════════════════════════════════════════════════

# ── Person 1: Incident & Safety Routes (MOCKED) ──────────
from incidents.mock_routes import router as incidents_router
app.include_router(incidents_router, prefix=f"{settings.API_PREFIX}/incidents", tags=["Incidents"])

# ── Person 2: AI Query Routes (MOCKED) ───────────────────
# Real logic is in ai_core.main.process_query (mocked for now)

# ── Person 3: Auth, Feedback, Notifications, Safety, Logs ─────
from backend.api.auth import router as auth_router
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])

from backend.api.users import router as users_router
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])

from backend.api.feedback import router as feedback_router
app.include_router(feedback_router, prefix=f"{settings.API_PREFIX}/feedback", tags=["Feedback"])

from backend.api.notifications import router as notifications_router
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])

from backend.api.query import router as query_router
app.include_router(query_router, prefix=f"{settings.API_PREFIX}/query", tags=["Query"])

from backend.api.safety import router as safety_router
app.include_router(safety_router, prefix=f"{settings.API_PREFIX}/safety", tags=["Safety"])

from backend.api.logs import router as logs_router
app.include_router(logs_router, prefix=f"{settings.API_PREFIX}/logs", tags=["Logs"])


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK & ROOT
# ═══════════════════════════════════════════════════════════

@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }



# ═══════════════════════════════════════════════════════════
# FRONTEND SERVING
# ═══════════════════════════════════════════════════════════

# Mount the frontend directory to serve index.html and assets
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
