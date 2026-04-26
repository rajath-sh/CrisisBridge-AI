from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MapBase(BaseModel):
    description: Optional[str] = None
    floor_number: Optional[int] = None

class MapCreate(MapBase):
    pass

class MapUpdate(MapBase):
    pass

class MapResponse(MapBase):
    id: str
    image_path: str
    uploaded_at: datetime
    uploaded_by: Optional[str]

    class Config:
        from_attributes = True
