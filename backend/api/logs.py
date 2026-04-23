"""
Logs API Routes for CrisisBridge AI
====================================
Endpoints:
- GET /query-logs
- GET /incident-logs
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from shared.dependencies import get_db, require_role
from shared.models import QueryLog, Incident, User
from shared.enums import UserRole

router = APIRouter()


@router.get(
    "/queries", 
    summary="Get AI query logs (Admin only)"
)
async def get_query_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns the most recent AI assistant queries and responses.
    """
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit).all()


@router.get(
    "/incidents", 
    summary="Get incident history logs (Admin only)"
)
async def get_incident_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns a history of all incidents reported in the system.
    """
    return db.query(Incident).order_by(Incident.reported_at.desc()).limit(limit).all()
