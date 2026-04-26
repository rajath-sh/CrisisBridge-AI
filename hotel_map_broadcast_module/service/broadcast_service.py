from sqlalchemy.orm import Session
from hotel_map_broadcast_module.models.broadcast_model import BroadcastMessage
from hotel_map_broadcast_module.realtime.broadcast_ws import manager
from hotel_map_broadcast_module.schemas.broadcast_schema import BroadcastCreate
from backend.services.notifications import broadcast_message
from shared.enums import NotificationType

class BroadcastService:
    @staticmethod
    async def create_broadcast(db: Session, broadcast_in: BroadcastCreate, creator: str):
        new_msg = BroadcastMessage(
            message=broadcast_in.message,
            priority=broadcast_in.priority,
            created_by=creator
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)

        # 1. Trigger database notification for all users
        try:
            broadcast_message(
                db, 
                title=f"New Announcement ({broadcast_in.priority.upper()})", 
                message=broadcast_in.message,
                notif_type=NotificationType.BROADCAST
            )
        except Exception as e:
            print(f"Failed to create notifications for broadcast: {e}")

        # 2. Trigger real-time alert via WebSocket
        await manager.broadcast({
            "id": new_msg.id,
            "message": new_msg.message,
            "priority": new_msg.priority,
            "created_at": new_msg.created_at.isoformat() + "Z"
        })
        
        return new_msg

    @staticmethod
    def get_all_broadcasts(db: Session):
        return db.query(BroadcastMessage).order_by(BroadcastMessage.created_at.desc()).all()

    @staticmethod
    def delete_broadcast(db: Session, broadcast_id: str):
        db_msg = db.query(BroadcastMessage).filter(BroadcastMessage.id == broadcast_id).first()
        if db_msg:
            db.delete(db_msg)
            db.commit()
            return True
        return False
