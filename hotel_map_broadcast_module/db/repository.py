from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hotel_map_broadcast_module.config.settings import settings
from hotel_map_broadcast_module.models.map_model import Base

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
