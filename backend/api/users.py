"""
User API Routes for CrisisBridge AI
====================================
Endpoints:
- PATCH /me/location
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.dependencies import get_db, get_current_active_user
from shared.schemas import UserLocationUpdate, UserResponse
from shared.models import User

router = APIRouter()


@router.patch(
    "/me/location", 
    response_model=UserResponse,
    summary="Update current user location"
)
async def update_location(
    data: UserLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates the floor, room, and zone for the current user.
    Used for proximity-based safety checks.
    """
    if data.current_floor is not None:
        current_user.current_floor = data.current_floor
    if data.current_room is not None:
        current_user.current_room = data.current_room
    if data.current_zone is not None:
        current_user.current_zone = data.current_zone
        
    db.commit()
    db.refresh(current_user)
    return UserResponse.from_orm(current_user)
