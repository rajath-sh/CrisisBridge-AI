from pydantic import BaseModel

class IncidentCreate(BaseModel):
    type: str
    latitude: float
    longitude: float

class IncidentStatusUpdate(BaseModel):
    incident_id: int
    status: str

class SafetyRequest(BaseModel):
    user_lat: float
    user_lon: float