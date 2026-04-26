import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HotelMap(Base):
    __tablename__ = "hotel_maps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_path = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    floor_number = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), nullable=True)

class HotelLocation(Base):
    __tablename__ = "hotel_locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    floor = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
