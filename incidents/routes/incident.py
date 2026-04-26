from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.dependencies import get_db
from ..schemas import IncidentCreate, IncidentStatusUpdate
from ..services import create_incident, fetch_incidents, update_incident_status
from shared.enums import IncidentStatus
import os
import shutil
import uuid
from fastapi import File, UploadFile
from ..database_extra import get_db_extra, init_extra_db
from ..models_extra import IncidentExtra
from sqlalchemy.orm import Session as SessionType
from backend.services import notifications as notif_service
from hotel_map_broadcast_module.realtime.broadcast_ws import manager
from shared.enums import NotificationType, UserRole
from shared.dependencies import get_current_user
from shared.models import User
import datetime

UPLOAD_DIR = os.path.join("incidents", "uploads", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/report")
async def report_incident(
    data: IncidentCreate, 
    db: Session = Depends(get_db),
    db_extra: SessionType = Depends(get_db_extra)
):
    try:
        # 1. Save to main shared DB
        incident = create_incident(db, data)
        
        # 2. Save extras to local DB
        extra = IncidentExtra(
            incident_id=incident.id,
            phone_number=data.phone_number,
            image_url=data.image_url
        )
        db_extra.add(extra)
        db_extra.commit()
        
        # 3. Trigger Real-time Notification
        notif_title = f"New {data.incident_type.upper()} Incident"
        notif_msg = f"{data.title} reported at {data.zone or 'Unknown'}. Severity: {data.severity.value.upper() if hasattr(data.severity, 'value') else str(data.severity).upper()}"
        
        # Save to DB history
        try:
            notif_service.broadcast_message(db, notif_title, notif_msg, NotificationType.INCIDENT_ALERT)
        except Exception:
            pass  # Non-critical, don't fail the whole request
        
        # Send WebSocket alert (async-safe)
        try:
            severity_val = data.severity.value if hasattr(data.severity, 'value') else str(data.severity)
            await manager.broadcast({
                "id": str(uuid.uuid4()),
                "message": notif_msg,
                "priority": "high" if severity_val in ["high", "critical"] else "normal",
                "created_at": datetime.datetime.utcnow().isoformat() + "Z"
            })
        except Exception:
            pass  # Non-critical, don't fail the whole request
        
        return {
            "success": True,
            "data": {"id": incident.id},
            "message": "Incident reported"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-image")
async def upload_incident_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"image_url": f"/api/v1/incidents/images/{filename}"}

@router.get("/images/{filename}")
async def get_incident_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    from fastapi.responses import FileResponse
    return FileResponse(file_path)

@router.get("/")
def read_incidents(
    db: Session = Depends(get_db),
    db_extra: SessionType = Depends(get_db_extra),
    current_user: User = Depends(get_current_user)
):
    incidents = fetch_incidents(db)
    print(f"DEBUG: Fetched {len(incidents)} incidents from shared DB")
    
    # Fetch all extras to merge
    extras = {e.incident_id: e for e in db_extra.query(IncidentExtra).all()}
    
    # Merge extras into response data
    merged_incidents = []
    for inc in incidents:
        inc_data = {
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "incident_type": inc.incident_type.value if hasattr(inc.incident_type, 'value') else str(inc.incident_type),
            "severity": inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity),
            "status": inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
            "floor": inc.floor,
            "room": inc.room,
            "zone": inc.zone,
            "reported_at": (inc.reported_at.isoformat() + "Z") if inc.reported_at else None,
            "reporter_name": inc.reporter.full_name or inc.reporter.username if inc.reporter else "Anonymous",
            "image_url": None,
            "phone_number": None
        }
        
        extra = extras.get(inc.id)
        if extra:
            inc_data["image_url"] = extra.image_url
            # Only expose phone number to staff/admin
            user_role = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
            if user_role in ['staff', 'admin']:
                inc_data["phone_number"] = extra.phone_number
        
        merged_incidents.append(inc_data)

    active_count = len([i for i in incidents if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
    return {
        "success": True,
        "incidents": merged_incidents,
        "active_count": active_count,
        "resolved_today": 0,
        "message": "All incidents with extras"
    }

@router.post("/update-status")
def update_status(data: IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = update_incident_status(db, data.incident_id, data.status)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "success": True,
        "data": {"id": incident.id, "status": incident.status},
        "message": "Status updated"
    }
