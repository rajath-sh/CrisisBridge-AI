"""
Shared Database Setup for CrisisBridge AI
===========================================
Provides:
- SQLAlchemy engine and session factory
- Base class for all ORM models
- get_db dependency for FastAPI routes

Used by ALL team members. DO NOT create separate engines.

Usage in routes:
    from shared.dependencies import get_db
    
    @router.get("/items")
    async def get_items(db: Session = Depends(get_db)):
        ...

Usage for models:
    from shared.database import Base
    
    class MyModel(Base):
        __tablename__ = "my_table"
        ...
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.config import settings

# ── Engine ───────────────────────────────────────
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL.lower() else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    connect_args=connect_args
)

# ── Session Factory ──────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Base class for all ORM models ────────────────
Base = declarative_base()


def init_db():
    """
    Create all tables defined by models that inherit from Base.
    Call this once at application startup.
    
    IMPORTANT: All model files must be imported before calling this,
    otherwise their tables won't be created.
    """
    # Import all models here so they register with Base.metadata
    import shared.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
