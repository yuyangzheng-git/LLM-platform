"""
API smoke tests using FastAPI TestClient (no external services required).
Run: python -m pytest tests/ -v  (from the backend directory)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["app"] == "LLM Chat Platform"


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "docs" in response.json()


def test_models_endpoint_shape():
    with TestClient(app) as client:
        response = client.get("/api/v1/models/configs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_openapi_schema_generated():
    # /openapi.json is only served in debug mode; build the schema directly
    schema = app.openapi()
    assert "/api/v1/chat" in str(schema["paths"].keys())
    assert "/api/v1/files" in str(schema["paths"].keys())
