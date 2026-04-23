"""
MOCK Incident Routes for CrisisBridge AI
==========================================
Temporary mock routes for Person 1's work to allow immediate integration.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime

from shared.dependencies import get_db, get_current_active_user
from shared.schemas import IncidentCreate, IncidentResponse, IncidentListResponse
from shared.models import Incident, User
from shared.enums import IncidentStatus, IncidentPriority

router = APIRouter()

@router.post("/report", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """MOCK: Report a new incident."""
    new_incident = Incident(
        incident_type=data.incident_type,
        severity=data.severity,
        priority=IncidentPriority.P2, # Simplified logic for mock
        status=IncidentStatus.REPORTED,
        title=data.title,
        description=data.description,
        floor=data.floor,
        room=data.room,
        zone=data.zone,
        reporter_id=current_user.id
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident

@router.get("", response_model=IncidentListResponse)
async def list_incidents(db: Session = Depends(get_db)):
    """MOCK: List all incidents."""
    incidents = db.query(Incident).all()
    return IncidentListResponse(
        incidents=incidents,
        total=len(incidents),
        active_count=sum(1 for i in incidents if i.status != IncidentStatus.RESOLVED)
    )
