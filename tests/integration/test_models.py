import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models import get_model_provider, ModelError

client = TestClient(app)


@pytest.mark.asyncio
async def test_provider_health_locally():
    provider = get_model_provider()
    health = await provider.health()
    assert health.reachable is True
    assert health.provider == "ollama"
    assert len(health.installed_models) > 0


@pytest.mark.asyncio
async def test_qwen25_coder_reachable_and_generates():
    provider = get_model_provider()
    # Verified coding test request
    res = await provider.generate(
        model="qwen2.5-coder:3b",
        prompt="Write a Python function named `add_numbers` that returns the sum of two integers.",
        options={"temperature": 0.1, "num_predict": 128}
    )
    assert res.done is True
    assert "add_numbers" in res.content
    assert res.latency_ms > 0


@pytest.mark.asyncio
async def test_qwen3_reasoning_reachable_and_generates():
    provider = get_model_provider()
    # Verified reasoning / general test request
    res = await provider.generate(
        model="qwen3:4b",
        prompt="In one sentence, explain what causes metal fatigue in industrial machinery.",
        options={"temperature": 0.1, "num_predict": 128}
    )
    assert res.done is True
    assert len(res.content.strip()) > 0
    assert res.latency_ms > 0


@pytest.mark.asyncio
async def test_gemma3_multimodal_reachable_and_generates():
    provider = get_model_provider()
    # Verified multimodal test request
    res = await provider.generate(
        model="gemma3:4b",
        prompt="State in 5 words or less what an optical character recognition (OCR) system does.",
        options={"temperature": 0.1, "num_predict": 64}
    )
    assert res.done is True
    assert len(res.content.strip()) > 0
    assert res.latency_ms > 0

    caps = await provider.capabilities("gemma3:4b")
    assert caps.supports_vision is True
    assert caps.verified is True


@pytest.mark.asyncio
async def test_unavailable_model_controlled_error():
    provider = get_model_provider()
    with pytest.raises(ModelError) as exc_info:
        await provider.generate(
            model="nonexistent-model-xyz",
            prompt="Hello"
        )
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.message.lower()


def test_api_models_health_endpoint():
    response = client.get("/api/models/health")
    assert response.status_code == 200
    data = response.json()
    assert data["reachable"] is True
    assert "qwen2.5-coder:3b" in data["installed_models"]


def test_api_models_capabilities_endpoint():
    response = client.get("/api/models/capabilities/qwen2.5-coder:3b")
    assert response.status_code == 200
    caps = response.json()
    assert caps["model"] == "qwen2.5-coder:3b"
    assert caps["verified"] is True
    assert "supports_streaming" in caps


def test_api_models_unavailable_model_returns_404():
    response = client.get("/api/models/capabilities/nonexistent-model-xyz")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
