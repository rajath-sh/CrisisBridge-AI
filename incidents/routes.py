from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from . import services, schemas

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🚨 Report Incident
@router.post("/report-incident")
def report_incident(data: schemas.IncidentCreate, db: Session = Depends(get_db)):
    incident = services.create_incident(db, data)
    return {
        "success": True,
        "data": {"id": incident.id},
        "message": "Incident reported"
    }

# 📍 Get Incidents
@router.get("/get-incidents")
def get_incidents(db: Session = Depends(get_db)):
    incidents = services.get_incidents(db)
    return {
        "success": True,
        "data": incidents,
        "message": "All incidents"
    }

# 🔄 Update Status
@router.post("/update-status")
def update_status(data: schemas.IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = services.update_incident_status(db, data.incident_id, data.status)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "success": True,
        "data": {"id": incident.id, "status": incident.status},
        "message": "Status updated"
    }

# 🛟 Safety Check
@router.post("/safety-check")
def safety_check(req: schemas.SafetyRequest, db: Session = Depends(get_db)):
    incidents = services.get_active_incidents(db)

    if not incidents:
        return {
            "success": True,
            "data": {"status": "SAFE"},
            "message": "No active incidents"
        }

    min_dist = float("inf")
    nearest = None

    for inc in incidents:
        dist = services.calculate_distance(
            req.user_lat, req.user_lon,
            inc.latitude, inc.longitude
        )
        if dist < min_dist:
            min_dist = dist
            nearest = inc

    status = services.get_safety_status(min_dist)

    return {
        "success": True,
        "data": {
            "status": status,
            "nearest_distance_km": round(min_dist, 2),
            "nearest_incident": {
                "id": nearest.id,
                "type": nearest.type
            }
        },
        "message": "Safety evaluated"
    }
