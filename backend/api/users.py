"""
User API Routes for CrisisBridge AI
====================================
Endpoints:
- PATCH /me/location
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.dependencies import get_db, get_current_active_user, require_role
from shared.schemas import UserLocationUpdate, UserResponse
from shared.models import User
from shared.enums import UserRole
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List

class RoleUpdate(BaseModel):
    role: UserRole

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


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Change a user's role (Admin Only)"
)
async def update_user_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Allows an admin to promote/demote users (e.g. Guest -> Staff).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.role = data.role
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.get(
    "/staff/online",
    response_model=List[UserResponse],
    summary="Get online staff and admins"
)
async def list_online_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns a list of staff and admins active in the last 5 minutes.
    """
    from datetime import datetime, timedelta
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    
    online_staff = db.query(User).filter(
        User.role == UserRole.STAFF,
        User.updated_at >= five_mins_ago,
        User.is_active == True
    ).all()
    
    return [UserResponse.from_orm(u) for u in online_staff]

@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users (Admin Only)"
)
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns a list of all registered users for admin management.
    """
    users = db.query(User).all()
    return [UserResponse.from_orm(u) for u in users]
