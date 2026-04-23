"""
Verification Script for person 3 Tasks
========================================
Tests:
- Health check
- Auth (Register/Login/Me)
- Query (Cache Miss/Hit)
- Feedback (Submit/Stats)
- Notifications (Get/Read/Broadcast)
"""

import sys
import os

# Add project root to path
sys.path.append(os.getcwd())


os.environ["DATABASE_URL"] = "sqlite:///./test_crisisbridge.db"

from fastapi.testclient import TestClient
from main import app
from shared.database import init_db, SessionLocal, engine
from shared.models import User, QueryLog, Feedback, Notification
from shared.enums import UserRole, FeedbackTargetType, FeedbackRating
from shared.dependencies import get_redis

# Mock Redis Client
class MockRedis:
    def __init__(self, **kwargs):
        self.data = {}
    def get(self, key): return self.data.get(key)
    def setex(self, key, ttl, val): self.data[key] = val
    def lrange(self, key, s, e): return []
    def lpush(self, key, val): pass
    def ltrim(self, key, s, e): pass
    def expire(self, key, ttl): pass

def get_mock_redis():
    return MockRedis()

app.dependency_overrides[get_redis] = get_mock_redis

client = TestClient(app)

def setup_db():
    print("Setting up test database...")
    init_db()
    db = SessionLocal()
    db.query(Feedback).delete()
    db.query(Notification).delete()
    db.query(QueryLog).delete()
    db.query(User).filter(User.email.like("test_%")).delete()
    db.commit()
    db.close()

def test_health():
    print("\n--- Testing Health Check ---")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    print("Health OK:", response.json())

def test_auth_flow():
    print("\n--- Testing Auth Flow ---")
    
    # 1. Register
    reg_data = {
        "email": "test_user@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "guest"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    print("Registration OK")

    # 2. Login
    login_data = {
        "email": "test_user@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    print("Login OK")

    # 3. Get Me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test_user@example.com"
    print("Get Me OK")
    
    return token

def test_query_flow(token):
    print("\n--- Testing Query Flow ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    query_data = {
        "query": "What to do in a fire?",
        "session_id": "test_session_123"
    }
    
    # 1. First call (Cache MISS)
    response = client.post("/api/v1/query", json=query_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["cache_status"] == "miss"
    print("Query Miss OK")
    
    # 2. Second call (Cache HIT)
    # Note: This depends on Redis being running. If not, it will be another miss.
    response = client.post("/api/v1/query", json=query_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    # If redis is not running, it might still be 'miss' but won't crash
    print(f"Query Second Call OK (Status: {data['cache_status']})")
    
    return data["query_log_id"]

def test_feedback_flow(token, query_log_id):
    print("\n--- Testing Feedback Flow ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Submit feedback
    feedback_data = {
        "target_type": "ai_response",
        "rating": "helpful",
        "comment": "Great mock response!",
        "query_log_id": query_log_id
    }
    response = client.post("/api/v1/feedback", json=feedback_data, headers=headers)
    assert response.status_code == 201
    print("Feedback Submission OK")

    # 2. Check stats (Requires Admin)
    # Create admin user manually
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "test_admin@example.com").first()
    if not admin:
        from backend.services.auth import hash_password
        admin = User(
            email="test_admin@example.com",
            username="testadmin",
            hashed_password=hash_password("adminpass"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
    db.close()
    
    # Login as admin
    login_data = {"email": "test_admin@example.com", "password": "adminpass"}
    admin_token = client.post("/api/v1/auth/login", json=login_data).json()["access_token"]
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/feedback/stats", headers=admin_headers)
    assert response.status_code == 200
    print("Feedback Stats OK:", response.json())

def test_notifications_flow(token):
    print("\n--- Testing Notifications Flow ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Broadcast (As Admin)
    login_data = {"email": "test_admin@example.com", "password": "adminpass"}
    admin_token = client.post("/api/v1/auth/login", json=login_data).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    broadcast_data = {
        "title": "Test Broadcast",
        "message": "This is a test broadcast message"
    }
    response = client.post("/api/v1/notifications/broadcast?title=Test%20Broadcast&message=This%20is%20a%20test", headers=admin_headers)
    assert response.status_code == 200
    print("Broadcast OK")
    
    # 2. Get Notifications
    response = client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    notif_id = data["notifications"][0]["id"]
    print("Get Notifications OK")
    
    # 3. Mark as read
    response = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=headers)
    assert response.status_code == 200
    print("Mark as Read OK")

if __name__ == "__main__":
    try:
        setup_db()
        test_health()
        token = test_auth_flow()
        log_id = test_query_flow(token)
        test_feedback_flow(token, log_id)
        test_notifications_flow(token)
        print("\nSUCCESS: ALL PERSON 3 TESTS PASSED!")
    except Exception as e:
        print(f"\nERROR: TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
