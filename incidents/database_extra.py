import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models_extra import Base

DB_PATH = os.path.join(os.path.dirname(__file__), "incidents_extra.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocalExtra = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_extra_db():
    Base.metadata.create_all(bind=engine)

def get_db_extra():
    db = SessionLocalExtra()
    try:
        yield db
    finally:
        db.close()
