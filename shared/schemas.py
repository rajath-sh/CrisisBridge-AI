"""
Shared Pydantic Schemas for CrisisBridge AI
=============================================
ALL request/response schemas for every API endpoint.
Used by ALL team members — this is the SHARED CONTRACT.

Rules:
- NEVER define Pydantic models in your own module for API I/O.
- If you need a new schema, add it HERE and inform the team.
- Group schemas by feature area.

Naming Convention:
- *Create   → POST request body
- *Update   → PUT/PATCH request body
- *Response → API response body
- *Base     → Shared fields (not used directly in APIs)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from shared.enums import (
    UserRole, IncidentType, IncidentSeverity, IncidentStatus,
    IncidentPriority, SafetyLevel, CacheStatus,
    FeedbackRating, FeedbackTargetType, NotificationType,
    QueryCategory
)


# ═══════════════════════════════════════════════════════════
#  AUTH & USER SCHEMAS
#  API Owner: Person 3
#  Used by: ALL
# ═══════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    """POST /api/v1/auth/register"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.GUEST


class UserLogin(BaseModel):
    """POST /api/v1/auth/login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response from login/register"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """User data returned in API responses"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: UserRole
    current_floor: Optional[int] = None
    current_room: Optional[str] = None
    current_zone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLocationUpdate(BaseModel):
    """PATCH /api/v1/users/me/location — update user's current location"""
    current_floor: Optional[int] = None
    current_room: Optional[str] = None
    current_zone: Optional[str] = None


class UserDetailsUpdate(BaseModel):
    """PATCH /api/v1/auth/me/details"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserPasswordUpdate(BaseModel):
    """PATCH /api/v1/auth/me/password"""
    current_password: str
    new_password: str = Field(..., min_length=6)


# ═══════════════════════════════════════════════════════════
#  INCIDENT SCHEMAS
#  API Owner: Person 1
#  Used by: ALL (dashboard, alerts, safety)
# ═══════════════════════════════════════════════════════════

class IncidentCreate(BaseModel):
    """POST /api/v1/incidents/report — Panic button / incident report"""
    incident_type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    title: str = Field(..., min_length=5, max_length=300)
    description: Optional[str] = None
    floor: Optional[int] = None
    room: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class IncidentUpdate(BaseModel):
    """PATCH /api/v1/incidents/{id}/status — Update incident status"""
    status: Optional[IncidentStatus] = None
    assigned_staff_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    severity: Optional[IncidentSeverity] = None


class IncidentResponse(BaseModel):
    """Single incident in API responses"""
    id: int
    incident_type: IncidentType
    severity: IncidentSeverity
    priority: IncidentPriority
    status: IncidentStatus
    title: str
    description: Optional[str] = None
    floor: Optional[int] = None
    room: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reporter_id: int
    reporter_name: Optional[str] = None
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None
    reported_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """GET /api/v1/incidents — List of incidents"""
    incidents: list[IncidentResponse]
    total: int
    active_count: int  # Non-resolved/closed count


class IncidentStats(BaseModel):
    """GET /api/v1/incidents/stats — Dashboard statistics"""
    total_incidents: int
    active_incidents: int
    resolved_today: int
    avg_resolution_time_minutes: Optional[float] = None
    by_type: dict[str, int] = {}    # {"fire": 3, "medical": 5}
    by_status: dict[str, int] = {}  # {"reported": 2, "responding": 1}
    by_severity: dict[str, int] = {}


# ═══════════════════════════════════════════════════════════
#  SAFETY CHECK SCHEMAS
#  API Owner: Person 1
#  Used by: ALL (guests check safety, dashboard shows zones)
# ═══════════════════════════════════════════════════════════

class SafetyCheckRequest(BaseModel):
    """POST /api/v1/safety/check — Check safety at a location"""
    floor: Optional[int] = None
    room: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SafetyCheckResponse(BaseModel):
    """Response from safety check"""
    safety_level: SafetyLevel
    message: str  # "You are in a safe zone" / "Warning: incident nearby"
    nearby_incidents: list[IncidentResponse] = []
    recommended_action: str  # "Stay calm" / "Move to nearest exit"
    nearest_exit: Optional[str] = None
    checked_at: datetime


# ═══════════════════════════════════════════════════════════
#  AI QUERY SCHEMAS
#  API Owner: Person 3 (route) + Person 2 (processing)
#  Used by: ALL (chat UI, SOP, guidance)
# ═══════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """POST /api/v1/query — Send question to AI assistant"""
    query: str = Field(..., min_length=2, max_length=2000)
    session_id: Optional[str] = None  # For session memory continuity
    category: Optional[QueryCategory] = None  # Optional hint for routing


class QueryResponse(BaseModel):
    """Response from AI assistant — THE CORE OUTPUT FORMAT"""
    answer: str
    sources: list[str] = []       # List of source document references
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str              # Agent explanation of reasoning
    cache_status: CacheStatus     # Whether served from cache
    response_time_ms: float       # Processing time
    session_id: Optional[str] = None
    query_log_id: Optional[int] = None  # Reference for feedback


# ═══════════════════════════════════════════════════════════
#  FEEDBACK SCHEMAS
#  API Owner: Person 3
#  Used by: ALL (AI chat feedback, incident response feedback)
# ═══════════════════════════════════════════════════════════

class FeedbackCreate(BaseModel):
    """POST /api/v1/feedback — Submit feedback"""
    target_type: FeedbackTargetType
    rating: FeedbackRating
    comment: Optional[str] = Field(None, max_length=1000)
    query_log_id: Optional[int] = None    # If rating an AI response
    incident_id: Optional[int] = None     # If rating incident handling


class FeedbackResponse(BaseModel):
    """Feedback item in responses"""
    id: int
    user_id: int
    target_type: FeedbackTargetType
    rating: FeedbackRating
    comment: Optional[str] = None
    query_log_id: Optional[int] = None
    incident_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """GET /api/v1/feedback/stats — Aggregated feedback metrics"""
    total_feedbacks: int
    helpful_count: int
    not_helpful_count: int
    helpful_percentage: float
    recent_comments: list[str] = []


# ═══════════════════════════════════════════════════════════
#  NOTIFICATION SCHEMAS
#  API Owner: Person 3 (delivery) + Person 1 (trigger)
#  Used by: ALL frontends
# ═══════════════════════════════════════════════════════════

class NotificationCreate(BaseModel):
    """Internal schema — used by backend to create notifications"""
    user_id: int
    notification_type: NotificationType
    title: str
    message: str
    incident_id: Optional[int] = None


class NotificationResponse(BaseModel):
    """Single notification in API responses"""
    id: int
    notification_type: NotificationType
    title: str
    message: str
    incident_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """GET /api/v1/notifications — User's notifications"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


# ═══════════════════════════════════════════════════════════
#  COMMON / UTILITY SCHEMAS
#  Used by: ALL
# ═══════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """GET /api/v1/health"""
    status: str = "ok"
    version: str
    database: str = "connected"
    redis: str = "connected"
    faiss: str = "loaded"


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    detail: Optional[str] = None
    status_code: int


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class MessageResponse(BaseModel):
    """Generic success message"""
    message: str
    success: bool = True


# ═══════════════════════════════════════════════════════════
#  AI CORE INTERFACE SCHEMA
#  This is the contract between Person 2 and Person 3
#  Person 2's ai_core.process() MUST return this format
# ═══════════════════════════════════════════════════════════

class AIProcessRequest(BaseModel):
    """
    Input to ai_core.process()
    Person 3 constructs this and sends to Person 2's pipeline.
    """
    query: str
    session_id: Optional[str] = None
    session_history: list[dict] = []  # Last N query-answer pairs
    category: Optional[QueryCategory] = None


class AIProcessResponse(BaseModel):
    """
    Output from ai_core.process()
    Person 2's pipeline MUST return this format.
    Person 3 wraps this into QueryResponse for the API.
    """
    answer: str
    sources: list[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    rewritten_query: Optional[str] = None  # The query after rewriting agent
    agent_trace: Optional[dict] = None     # Debug info about agent execution


# Forward reference resolution
TokenResponse.model_rebuild()
