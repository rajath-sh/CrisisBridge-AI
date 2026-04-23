"""
Safety API Routes for CrisisBridge AI
=======================================
Endpoints:
- POST /check
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.dependencies import get_db, get_current_active_user
from shared.schemas import SafetyCheckRequest, SafetyCheckResponse
from shared.models import User
from backend.services import safety as safety_service

router = APIRouter()


@router.post(
    "/check", 
    response_model=SafetyCheckResponse,
    summary="Check safety status at a location"
)
async def check_safety(
    request: SafetyCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Evaluates risk based on the user's current location and active incidents.
    Returns safety level (Safe/Warning/Evacuate) and recommended actions.
    """
    return safety_service.check_safety(db, request)
