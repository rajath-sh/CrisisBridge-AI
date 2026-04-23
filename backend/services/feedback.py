"""
Feedback Service for CrisisBridge AI
======================================
Handles user feedback for AI responses and incident coordination.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from shared.models import Feedback, QueryLog, User
from shared.schemas import FeedbackCreate, FeedbackStats
from shared.enums import FeedbackRating


def create_feedback(db: Session, user_id: int, data: FeedbackCreate) -> Feedback:
    """
    Creates a new feedback entry.
    """
    new_feedback = Feedback(
        user_id=user_id,
        target_type=data.target_type,
        query_log_id=data.query_log_id,
        incident_id=data.incident_id,
        rating=data.rating,
        comment=data.comment
    )
    
    try:
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return new_feedback
    except Exception as e:
        logger.error(f"Failed to create feedback: {e}")
        db.rollback()
        raise


def get_feedback_stats(db: Session) -> FeedbackStats:
    """
    Calculates feedback metrics for admin dashboard.
    """
    total = db.query(Feedback).count()
    
    helpful = db.query(Feedback).filter(
        Feedback.rating == FeedbackRating.HELPFUL
    ).count()
    
    not_helpful = total - helpful
    
    percentage = (helpful / total * 100) if total > 0 else 0.0
    
    recent = db.query(Feedback.comment).filter(
        Feedback.comment != None
    ).order_by(
        Feedback.created_at.desc()
    ).limit(10).all()
    
    return FeedbackStats(
        total_feedbacks=total,
        helpful_count=helpful,
        not_helpful_count=not_helpful,
        helpful_percentage=percentage,
        recent_comments=[r[0] for r in recent]
    )
