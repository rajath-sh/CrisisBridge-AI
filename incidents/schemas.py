from pydantic import BaseModel
from typing import Optional
from shared.enums import IncidentType, IncidentSeverity

class IncidentCreate(BaseModel):
    title: str
    incident_type: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    description: Optional[str] = None
    floor: Optional[int] = None
    room: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reporter_id: int
    phone_number: str
    image_url: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    incident_id: int
    status: str

class SafetyRequest(BaseModel):
    user_lat: float
    user_lon: float
