import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import SessionLocal
from shared.models import Incident
from incidents.models_extra import IncidentExtra
from incidents.database_extra import SessionLocalExtra

def check_incidents():
    try:
        db = SessionLocal()
        print("--- SHARED DB INCIDENTS ---")
        incidents = db.query(Incident).order_by(Incident.id.desc()).limit(10).all()
        for inc in incidents:
            print(f"ID: {inc.id}, Title: {inc.title}, Type: {inc.incident_type}, Status: {inc.status}, Reported: {inc.reported_at}")
    except Exception as e:
        print("Error fetching from Shared DB:")
        traceback.print_exc()

    try:
        db_extra = SessionLocalExtra()
        print("\n--- EXTRA DB INCIDENTS ---")
        extras = db_extra.query(IncidentExtra).order_by(IncidentExtra.incident_id.desc()).limit(10).all()
        for e in extras:
            print(f"Incident ID: {e.incident_id}, Phone: {e.phone_number}, Image: {e.image_url}")
    except Exception as e:
        print("Error fetching from Extra DB:")
        traceback.print_exc()

if __name__ == "__main__":
    check_incidents()
