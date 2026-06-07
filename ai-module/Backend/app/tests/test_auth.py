import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal
from app.models.admin import Admin
from app.utils.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_admin():
    """Create a test admin account for testing auth flow."""
    db = SessionLocal()
    # Clean up existing test admin
    db.query(Admin).filter(Admin.username == "test_auth_admin").delete()
    
    # Create new test admin with hashed password
    test_admin = Admin(
        username="test_auth_admin",
        password=get_password_hash("securepassword123")
    )
    db.add(test_admin)
    db.commit()
    db.close()

def test_login_success():
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_auth_admin", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["username"] == "test_auth_admin"

def test_login_invalid_password():
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_auth_admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    # Updated to match our custom error handler format
    assert "Invalid username or password" in response.json()["message"]

def test_protected_route_unauthorized():
    """Test accessing a protected route without a token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    # Updated to match our custom error handler format
    assert "Not authenticated" in response.json()["message"]

def test_protected_route_success():
    """Test accessing a protected route with a valid token."""
    # 1. Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_auth_admin", "password": "securepassword123"}
    )
    token = login_response.json()["access_token"]
    
    # 2. Access protected route with Bearer token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_auth_admin"

def test_logout():
    """Test logout response format."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Logged Out Successfully" in response.json()["message"]
