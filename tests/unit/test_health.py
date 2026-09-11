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

    # Model infrastructure is READY for Phase 1
    assert subsystems["model_infrastructure"]["status"] == "READY"
    assert subsystems["model_infrastructure"]["phase"] == 1

    # Model registry is READY for Phase 2
    assert subsystems["model_registry"]["status"] == "READY"
    assert subsystems["model_registry"]["phase"] == 2

    # Task router is READY for Phase 3
    assert subsystems["task_router"]["status"] == "READY"
    assert subsystems["task_router"]["phase"] == 3

    # Agent orchestrator is READY for Phase 4
    assert subsystems["agent_orchestrator"]["status"] == "READY"
    assert subsystems["agent_orchestrator"]["phase"] == 4

    # Tool registry is READY for Phase 5
    assert subsystems["tool_registry"]["status"] == "READY"
    assert subsystems["tool_registry"]["phase"] == 5

    # Sandbox must NOT falsely claim completion
    assert subsystems["sandbox"]["status"] == "PENDING"
    assert subsystems["sandbox"]["phase"] == 6
