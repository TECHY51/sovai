import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.router import get_task_router, RoutingRequest, TaskType

client = TestClient(app)


def test_api_route_coding_request():
    payload = {
        "prompt": "Write a Python script that parses CSV files and handles exceptions."
    }
    response = client.post("/api/router/route", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["task_type"] == "coding"
    assert data["model_id"] == "qwen2.5-coder-3b"
    assert data["model_tag"] == "qwen2.5-coder:3b"
    assert "python_sandbox" in data["tools"]
    assert data["confidence"] >= 0.70
    assert data["fallback_used"] is False


def test_api_route_reasoning_request():
    payload = {
        "prompt": "Analyze the industrial SOP compliance procedure and evaluate safety guidelines."
    }
    response = client.post("/api/router/route", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["task_type"] == "reasoning"
    assert data["model_id"] == "qwen3-4b"
    assert data["model_tag"] == "qwen3:4b"
    assert "search_documents" in data["tools"]
    assert data["confidence"] >= 0.70


def test_api_route_vision_request():
    payload = {
        "prompt": "Inspect this scanned engineering drawing and analyze the P&ID piping layout."
    }
    response = client.post("/api/router/route", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["task_type"] == "vision"
    assert data["model_id"] == "gemma3-4b"
    assert data["model_tag"] == "gemma3:4b"
    assert "analyze_image" in data["tools"]


def test_api_route_ambiguous_request():
    payload = {
        "prompt": "hi"
    }
    response = client.post("/api/router/route", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["task_type"] == "ambiguous"
    assert data["clarification_needed"] is True
    assert data["clarification_prompt"] is not None


def test_api_router_history_and_mappings():
    # Fetch mappings
    mappings_res = client.get("/api/router/mappings")
    assert mappings_res.status_code == 200
    mappings = mappings_res.json()
    assert "coding" in mappings["preferred_models"]
    assert mappings["preferred_models"]["coding"] == "qwen2.5-coder-3b"

    # Fetch history
    history_res = client.get("/api/router/history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert "timestamp" in history[-1]


def test_health_reports_task_router_ready():
    response = client.get("/api/health")
    assert response.status_code == 200
    subsystems = response.json()["subsystems"]
    assert "task_router" in subsystems
    assert subsystems["task_router"]["status"] == "READY"
    assert subsystems["task_router"]["phase"] == 3
