from sqlalchemy.orm import Session
from .models import Incident

def create_incident(db: Session, incident):
    new_incident = Incident(
        type=incident.type,
        latitude=incident.latitude,
        longitude=incident.longitude
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident

def get_incidents(db: Session):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()

def get_active_incidents(db: Session):
    return db.query(Incident).filter(Incident.status == "active").all()

def update_incident_status(db: Session, incident_id, status):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident:
        incident.status = status
        db.commit()
        db.refresh(incident)
    return incident