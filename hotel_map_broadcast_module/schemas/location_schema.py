from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LocationCreate(BaseModel):
    name: str
    floor: Optional[int] = None

class LocationResponse(BaseModel):
    id: str
    name: str
    floor: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
