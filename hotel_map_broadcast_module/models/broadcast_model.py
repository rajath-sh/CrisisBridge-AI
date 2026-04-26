import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from .map_model import Base

class BroadcastMessage(Base):
    __tablename__ = "broadcast_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False, default="normal") # low, normal, high
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
