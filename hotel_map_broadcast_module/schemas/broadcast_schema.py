from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BroadcastBase(BaseModel):
    message: str
    priority: str = "normal"

class BroadcastCreate(BroadcastBase):
    pass

class BroadcastResponse(BroadcastBase):
    id: str
    created_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True
