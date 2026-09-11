import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models import get_model_provider, get_model_registry, ModelStatus

client = TestClient(app)


@pytest.mark.asyncio
async def test_registry_live_provider_synchronization():
    registry = get_model_registry()
    provider = get_model_provider()

    # Synchronize availability against live local Ollama
    await registry.sync_availability(provider)

    # All three target models must be AVAILABLE on the local machine
    coder = registry.get_model("qwen2.5-coder-3b")
    assert coder is not None
    assert coder.status == ModelStatus.AVAILABLE

    reasoner = registry.get_model("qwen3-4b")
    assert reasoner is not None
    assert reasoner.status == ModelStatus.AVAILABLE

    vision = registry.get_model("gemma3-4b")
    assert vision is not None
    assert vision.status == ModelStatus.AVAILABLE

    # Configured unavailable model must be identified as UNAVAILABLE
    offline = registry.get_model("offline-test-model")
    assert offline is not None
    assert offline.status == ModelStatus.UNAVAILABLE

    # Available and unavailable queries
    available_ids = [m.id for m in registry.get_available_models()]
    assert "qwen2.5-coder-3b" in available_ids
    assert "qwen3-4b" in available_ids
    assert "gemma3-4b" in available_ids
    assert "offline-test-model" not in available_ids

    unavailable_ids = [m.id for m in registry.get_unavailable_models()]
    assert "offline-test-model" in unavailable_ids


def test_api_list_registry_models():
    response = client.get("/api/models/registry")
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 4
    model_ids = [m["id"] for m in models]
    assert "qwen2.5-coder-3b" in model_ids
    assert "qwen3-4b" in model_ids
    assert "gemma3-4b" in model_ids


def test_api_get_registry_model_by_id():
    response = client.get("/api/models/registry/qwen2.5-coder-3b")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "qwen2.5-coder-3b"
    assert data["type"] == "coding"
    assert data["capabilities"]["supports_tools"] is True
    assert data["status"] == "available"


def test_api_get_nonexistent_registry_model_returns_404():
    response = client.get("/api/models/registry/unknown-model-12345")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_api_registry_sync_endpoint():
    response = client.post("/api/models/registry/sync")
    assert response.status_code == 200
    summary = response.json()
    assert summary["status"] == "synchronized"
    assert summary["available_count"] >= 3
    assert "qwen2.5-coder-3b" in summary["available_ids"]
    assert "offline-test-model" in summary["unavailable_ids"]
