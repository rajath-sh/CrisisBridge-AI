"""
Notification API Routes for CrisisBridge AI
=============================================
Endpoints:
- GET /notifications
- PATCH /notifications/{id}/read
- POST /notifications/broadcast
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from shared.dependencies import get_db, get_current_active_user, require_role
from shared.schemas import NotificationListResponse, NotificationResponse, MessageResponse, NotificationCreate
from shared.models import User
from shared.enums import UserRole, NotificationType
from backend.services import notifications as notif_service

router = APIRouter()


@router.get(
    "", 
    response_model=NotificationListResponse,
    summary="Get user notifications"
)
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns a list of notifications for the current user.
    """
    notifs = notif_service.get_user_notifications(db, current_user.id)
    unread_count = sum(1 for n in notifs if not n.is_read)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifs],
        total=len(notifs),
        unread_count=unread_count
    )


@router.patch(
    "/{notification_id}/read", 
    response_model=MessageResponse,
    summary="Mark notification as read"
)
async def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Marks a notification as read.
    """
    success = notif_service.mark_as_read(db, current_user.id, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return MessageResponse(message="Notification marked as read")


@router.post(
    "/broadcast", 
    response_model=MessageResponse,
    summary="Broadcast message to all users (Admin only)"
)
async def broadcast(
    title: str,
    message: str,
    notif_type: NotificationType = NotificationType.BROADCAST,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Sends a notification to all active users in the system.
    """
    count = notif_service.broadcast_message(db, title, message, notif_type)
    return MessageResponse(message=f"Successfully broadcasted to {count} users")
