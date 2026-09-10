import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert data["health"] == "/api/health"


def test_health_endpoint_structure():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data
    assert isinstance(data["airgap_mode"], bool)
    assert "subsystems" in data


def test_subsystem_readiness_accuracy():
    response = client.get("/api/health")
    assert response.status_code == 200
    subsystems = response.json()["subsystems"]

    # Backend skeleton must be READY for Phase 0
    assert subsystems["api_backend"]["status"] == "READY"
    assert subsystems["api_backend"]["phase"] == 0

    # Model infrastructure must NOT falsely claim completion
    assert subsystems["model_infrastructure"]["status"] == "PENDING"
    assert subsystems["model_infrastructure"]["phase"] == 1

    # Router must NOT falsely claim completion
    assert subsystems["task_router"]["status"] == "PENDING"
    assert subsystems["task_router"]["phase"] == 3

    # Sandbox must NOT falsely claim completion
    assert subsystems["sandbox"]["status"] == "PENDING"
    assert subsystems["sandbox"]["phase"] == 6
