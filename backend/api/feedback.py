"""
Feedback API Routes for CrisisBridge AI
=========================================
Endpoints:
- POST /feedback
- GET /feedback/stats
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from shared.dependencies import get_db, get_current_active_user, require_role
from shared.schemas import FeedbackCreate, FeedbackResponse, FeedbackStats
from shared.models import User
from shared.enums import UserRole
from backend.services import feedback as feedback_service

router = APIRouter()


@router.post(
    "", 
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback"
)
async def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits feedback on an AI response or an incident response.
    """
    return feedback_service.create_feedback(db, current_user.id, data)


@router.get(
    "/stats", 
    response_model=FeedbackStats,
    summary="Get feedback statistics (Admin only)"
)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns aggregated feedback metrics. Restricted to Admin users.
    """
    return feedback_service.get_feedback_stats(db)
