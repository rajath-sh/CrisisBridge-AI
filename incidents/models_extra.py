from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IncidentExtra(Base):
    __tablename__ = "incident_extras"

    incident_id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False)
    image_url = Column(Text, nullable=True)
