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
    
    # 2. Check for matches in location
    for inc in active_incidents:
        is_nearby = False
        
        # Match by floor
        if request.floor and inc.floor == request.floor:
            is_nearby = True
        # Match by zone
        elif request.zone and inc.zone == request.zone:
            is_nearby = True
            
        if is_nearby:
            nearby.append(inc)
            # Escalate safety level based on severity
            if inc.severity == IncidentSeverity.CRITICAL:
                safety_level = SafetyLevel.EVACUATE
            elif inc.severity == IncidentSeverity.HIGH and safety_level != SafetyLevel.EVACUATE:
                safety_level = SafetyLevel.WARNING
            elif safety_level == SafetyLevel.SAFE:
                safety_level = SafetyLevel.WARNING

    # 3. Customize messages based on findings
    if safety_level == SafetyLevel.EVACUATE:
        message = "🚨 EVACUATE IMMEDIATELY!"
        recommended_action = "Follow emergency exit signs to the nearest assembly point."
    elif safety_level == SafetyLevel.WARNING:
        message = "⚠️ Caution: Active incident nearby."
        recommended_action = "Avoid affected areas and wait for staff instructions."
        
    return SafetyCheckResponse(
        safety_level=safety_level,
        message=message,
        nearby_incidents=nearby,
        recommended_action=recommended_action,
        checked_at=datetime.utcnow()
    )
