"""
Chat Module API Routes
========================
REST + WebSocket endpoints for the isolated chat module.

⚠️  ALL endpoints are ADMIN-ONLY in production (except /chat/start and /ws/chat).
    Add Depends(get_current_active_user) once auth is integrated.

REST Endpoints:
  POST   /chat/start                    — Guest starts a new chat session
  GET    /chat/sessions                 — List all sessions (admin)
  GET    /chat/messages/{session_id}    — Get message history
  PATCH  /chat/session/{session_id}/close — Close a session (admin)
  DELETE /chat/session/{session_id}     — Delete session + all messages (admin)
  GET    /chat/active                   — View live active connections (admin)

WebSocket:
  WS /ws/chat/{session_id}             — Real-time chat connection
"""

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from chat_module.db.repository import get_db, SessionLocal
from chat_module.db import repository
from chat_module.service import chat_service
from chat_module.schemas.chat_schema import StartChatRequest
from chat_module.connection.connection_manager import manager
from chat_module.websocket.ws_handler import handle_chat_connection

# ── Two routers: REST and WebSocket ──────────────────
rest_router = APIRouter(prefix="/chat", tags=["Chat — REST"])
ws_router   = APIRouter(prefix="/ws",   tags=["Chat — WebSocket"])


# ══════════════════════════════════════════════════════
#  REST ENDPOINTS
# ══════════════════════════════════════════════════════

@rest_router.post("/start", summary="Start a new chat session (guest)")
def start_chat(request: StartChatRequest, db: Session = Depends(get_db)):
    """
    Guest calls this to get a session_id.
    Then connects to WS /ws/chat/{session_id} with that ID.
    """
    return chat_service.start_session(db, user_id=request.user_id)


@rest_router.get("/sessions", summary="List all chat sessions (admin)")
def list_sessions(db: Session = Depends(get_db)):
    """(Admin) Returns all sessions ordered newest-first."""
    return chat_service.list_all_sessions(db)


@rest_router.get(
    "/messages/{session_id}",
    summary="Get message history for a session"
)
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Returns the full message history for a session (oldest-first)."""
    return chat_service.get_history(db, session_id)


@rest_router.patch(
    "/session/{session_id}/close",
    summary="Close a chat session (admin)"
)
def close_session(session_id: str, db: Session = Depends(get_db)):
    """
    (Admin) Marks the session as closed.
    Clients still connected via WebSocket will receive an error
    on their next message attempt.
    """
    return chat_service.close_session(db, session_id)


@rest_router.delete(
    "/session/{session_id}",
    summary="🗑️ Permanently delete a session + all its messages (admin)"
)
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    (Admin) Permanently deletes a session and ALL its messages from the database.
    This cannot be undone. Use close instead if you just want to end the session.
    """
    from chat_module.models.chat_models import ChatSession, ChatMessage

    # Disconnect any live participants gracefully
    if session_id in manager.active_connections:
        await manager.broadcast(session_id, {
            "event": "error",
            "message": "This session has been permanently deleted by an administrator."
        })

    # Delete messages first (foreign key order)
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    db.delete(session)
    db.commit()
    return {
        "status": "deleted",
        "session_id": session_id,
        "message": "Session and all messages permanently deleted."
    }


@rest_router.get("/active", summary="View live active WebSocket connections (admin)")
def active_connections(db: Session = Depends(get_db)):
    """
    (Admin) Shows which sessions currently have live WebSocket connections,
    including the originating user ID.
    """
    active_sessions = manager.get_all_active_sessions()
    
    valid_sessions = []
    for sid in active_sessions:
        session = repository.get_session(db, sid)
        if session:
            from chat_module.models.chat_models import ChatMessage
            msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == sid).count()
            
            valid_sessions.append({
                "session_id": sid,
                "user_id": session.user_id,
                "active_users": manager.get_active_count(sid),
                "message_count": msg_count
            })

    return {
        "total_active_sessions": len(valid_sessions),
        "sessions": valid_sessions
    }


# ══════════════════════════════════════════════════════
#  WEBSOCKET ENDPOINT
# ══════════════════════════════════════════════════════

@ws_router.websocket("/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    sender_id: str = "anonymous",
    sender_role: str = "guest"
):
    """
    Real-time chat WebSocket.

    Connect with query params:
        /ws/chat/{session_id}?sender_id=user_1&sender_role=guest
        /ws/chat/{session_id}?sender_id=staff_alice&sender_role=staff

    Send messages as JSON:
        { "sender_id": "user_1", "sender_role": "guest", "message": "Help!" }

    Receive broadcasts as JSON (event types):
        { "event": "message",     ... }
        { "event": "user_joined", ... }
        { "event": "user_left",   ... }
        { "event": "history",     ... }
        { "event": "error",       ... }
    """
    await handle_chat_connection(
        websocket=websocket,
        session_id=session_id,
        sender_id=sender_id,
        sender_role=sender_role
    )
