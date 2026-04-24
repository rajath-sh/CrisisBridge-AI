from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from services import get_active_incidents
from schemas import SafetyRequest
from utils.distance import calculate_distance, get_safety_status

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/safety-check")
def safety_check(req: SafetyRequest, db: Session = Depends(get_db)):
    incidents = get_active_incidents(db)

    if not incidents:
        return {
            "success": True,
            "data": {"status": "SAFE"},
            "message": "No active incidents"
        }

    min_dist = float("inf")
    nearest = None

    for inc in incidents:
        dist = calculate_distance(req.user_lat, req.user_lon, inc.latitude, inc.longitude)
        if dist < min_dist:
            min_dist = dist
            nearest = inc

    status = get_safety_status(min_dist)

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
