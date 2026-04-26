"""
Safety Service for CrisisBridge AI
====================================
Logic for checking risk levels based on user location vs active incidents.
"""

from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from shared.models import Incident, User
from shared.schemas import SafetyCheckRequest, SafetyCheckResponse
from shared.enums import SafetyLevel, IncidentStatus, IncidentSeverity


def check_safety(db: Session, request: SafetyCheckRequest) -> SafetyCheckResponse:
    """
    Determines safety level based on floor, room, and zone.
    (Simple zone-based logic for MVP)
    """
    # 1. Get all active (non-resolved) incidents
    active_incidents = db.query(Incident).filter(
        Incident.status != IncidentStatus.RESOLVED,
        Incident.status != IncidentStatus.CLOSED
    ).all()
    
    safety_level = SafetyLevel.SAFE
    message = "You are currently in a safe area."
    recommended_action = "Stay alert and follow standard safety protocols."
    nearby = []
    
    # 2. Check for matches in exact location (Zone/Room)
    for inc in active_incidents:
        is_exact_match = False
        
        # Clean strings for robust comparison
        req_zone = (request.zone or "").strip().lower()
        inc_zone = (inc.zone or "").strip().lower()
        
        # Match by zone (exact location)
        if req_zone and inc_zone == req_zone:
            is_exact_match = True
            
        if is_exact_match:
            nearby.append(inc)
            # For exact matches, we always use EVACUATE level to show RED color and high urgency
            safety_level = SafetyLevel.EVACUATE
        
        # Secondary warning for floor match
        elif request.floor and inc.floor == request.floor:
            nearby.append(inc)
            if safety_level == SafetyLevel.SAFE:
                safety_level = SafetyLevel.WARNING

    # 3. Customize messages based on findings
    if safety_level == SafetyLevel.EVACUATE:
        # Check if we have an exact match in the nearby list (robust check)
        req_zone = (request.zone or "").strip().lower()
        exact_matches = [inc for inc in nearby if (inc.zone or "").strip().lower() == req_zone]
        
        if exact_matches:
            message = f"🚨 ALERT: Emergency at {request.zone}!"
            recommended_action = "Please evacuate your current area immediately."
        else:
            message = "🚨 EVACUATE IMMEDIATELY!"
            recommended_action = "Follow emergency exit signs to the nearest assembly point."
    elif safety_level == SafetyLevel.WARNING:
        message = "⚠️ Caution: Active incident nearby on your floor."
        recommended_action = "Stay alert, avoid affected areas, and wait for further instructions."
        
    return SafetyCheckResponse(
        safety_level=safety_level,
        message=message,
        nearby_incidents=nearby,
        recommended_action=recommended_action,
        checked_at=datetime.utcnow()
    )
