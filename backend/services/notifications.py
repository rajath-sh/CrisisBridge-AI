"""
Notification Service for CrisisBridge AI
==========================================
Handles delivery of alerts and updates to users.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from shared.models import Notification, User
from shared.schemas import NotificationCreate, MessageResponse
from shared.enums import NotificationType


def create_notification(db: Session, data: NotificationCreate) -> Notification:
    """
    Creates a single notification for a specific user.
    """
    new_notif = Notification(
        user_id=data.user_id,
        notification_type=data.notification_type,
        title=data.title,
        message=data.message,
        incident_id=data.incident_id
    )
    
    try:
        db.add(new_notif)
        db.commit()
        db.refresh(new_notif)
        return new_notif
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        db.rollback()
        raise


def get_user_notifications(db: Session, user_id: int) -> List[Notification]:
    """
    Retrieves all notifications for a user, sorted by newest first.
    """
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()


def mark_as_read(db: Session, user_id: int, notification_id: int) -> bool:
    """
    Marks a specific notification as read.
    Returns True if successful, False if not found/unauthorized.
    """
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notif:
        return False
        
    notif.is_read = True
    db.commit()
    return True


def broadcast_message(db: Session, title: str, message: str, notif_type: NotificationType) -> int:
    """
    Sends a notification to ALL active users.
    Returns the count of notifications created.
    """
    active_users = db.query(User.id).filter(User.is_active == True).all()
    count = 0
    
    for (user_id,) in active_users:
        notif = Notification(
            user_id=user_id,
            notification_type=notif_type,
            title=title,
            message=message
        )
        db.add(notif)
        count += 1
        
    db.commit()
    logger.info(f"Broadcasted '{title}' to {count} users.")
    return count
