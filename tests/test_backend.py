import sys
import os
import pytest
from fastapi.testclient import TestClient

# Adjust path to import local packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.run import app
from backend.app.core.config import settings

client = TestClient(app)

def test_health_endpoint():
    """Verifies that the core health check api returns status healthy."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == settings.PROJECT_NAME

def test_auth_and_restricted_endpoints():
    """Verifies register, login, profile retrieval, and dashboard metrics endpoints."""
    # Test registration
    test_email = "test_scholar@researchmind.ai"
    # Clean previous if exists (since SQLite persists)
    from backend.app.db.session import SessionLocal
    from backend.app.db.models import User
    db = SessionLocal()
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    register_payload = {
        "email": test_email,
        "password": "securepassword123",
        "full_name": "Test Scholar User",
        "role": "Research Scholar"
    }
    
    reg_response = client.post(f"{settings.API_V1_STR}/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["email"] == test_email
    assert reg_data["role"] == "Research Scholar"

    # Test login
    login_payload = {
        "username": test_email,
        "password": "securepassword123"
    }
    
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_payload # OAuth2 password flow expects form data
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # Test profile access
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == test_email

    # Test dashboard statistics
    stats_response = client.get(f"{settings.API_V1_STR}/dashboard/stats", headers=headers)
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert "metrics" in stats_data
    # Confirms mock data was seeded
    assert stats_data["metrics"]["total_papers"] > 0

    # Test Knowledge Graph queries
    graph_response = client.get(f"{settings.API_V1_STR}/dashboard/graph", headers=headers)
    assert graph_response.status_code == 200
    graph_data = graph_response.json()
    assert "nodes" in graph_data
    assert "links" in graph_data
    assert len(graph_data["nodes"]) > 0

    print("\nAll integration test assertions passed successfully!")

if __name__ == "__main__":
    pytest.main([__file__])
