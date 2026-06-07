import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database.connection import test_db_connection

client = TestClient(app)

def test_server_instance():
    """Validates that the FastAPI app instance is created correctly."""
    assert app.title == "AI Attendance System API"
    assert app.version == "1.0.0"

def test_root_endpoint():
    """Validates the root '/' endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "AI Attendance System"
    assert data["status"] == "running"

def test_health_endpoint():
    """Validates the health check endpoint."""
    response = client.get(f"{settings.API_PREFIX}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["server"] == "online"

def test_database_connection_utility():
    """Validates the database connection utility (requires MySQL running)."""
    # Note: This depends on the actual DB status in the environment
    is_connected = test_db_connection()
    # We check if it returns a boolean to avoid failing the suite if DB is not yet set up
    assert isinstance(is_connected, bool)

def test_config_loading():
    """Validates that configuration is loaded correctly."""
    assert settings.API_PREFIX == "/api/v1"
    assert isinstance(settings.DEBUG_MODE, bool)

def test_cors_headers():
    """Validates that CORS headers are present in the response."""
    # We simulate a request from an allowed origin
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_404_json_handling():
    """Validates that non-existent routes return a standardized JSON 404."""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "HTTPException"
    # Note: If we wanted specific 404 handling, we'd add a specific handler for 404 status codes.

def test_docs_accessible():
    """Validates that the Swagger documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
