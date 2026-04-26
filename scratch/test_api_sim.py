import sys, os, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Simulate exactly what the API does so we can see the output
from shared.database import SessionLocal
from shared.models import Incident
from shared.enums import IncidentStatus
from incidents.models_extra import IncidentExtra
from incidents.database_extra import SessionLocalExtra

db = SessionLocal()
db_extra = SessionLocalExtra()

incidents = db.query(Incident).all()
extras = {e.incident_id: e for e in db_extra.query(IncidentExtra).all()}

merged = []
for inc in incidents:
    inc_data = {
        "id": inc.id,
        "title": inc.title,
        "incident_type": inc.incident_type.value if hasattr(inc.incident_type, 'value') else str(inc.incident_type),
        "severity": inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity),
        "status": inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
        "zone": inc.zone,
        "created_at": inc.reported_at.isoformat() if inc.reported_at else None,
    }
    merged.append(inc_data)

print("API RESPONSE (simulated):")
print(json.dumps({"incidents": merged, "active_count": len(merged)}, indent=2))

print("\nFILTERED (non-resolved):")
filtered = [i for i in merged if i["status"] not in ["resolved", "closed"]]
print(f"Count: {len(filtered)}")
for i in filtered:
    print(f"  - [{i['status']}] {i['title']} ({i['incident_type']})")
