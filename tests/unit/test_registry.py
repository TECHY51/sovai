import pytest
from pathlib import Path
from backend.app.models.registry import (
    ModelRegistry,
    ModelMetadata,
    ModelCategory,
    ModelStatus,
    ModelCapabilitiesInfo,
    RegistryConfigError
)
from backend.app.models import get_model_registry


def test_registry_loads_default_config():
    registry = get_model_registry()
    models = registry.list_models()
    assert len(models) >= 3

    coder = registry.get_model("qwen2.5-coder-3b")
    assert coder is not None
    assert coder.type == ModelCategory.CODING
    assert coder.tag == "qwen2.5-coder:3b"
    assert coder.capabilities.supports_tools is True
    assert coder.capabilities.supports_vision is False

    reasoner = registry.get_model("qwen3-4b")
    assert reasoner is not None
    assert reasoner.type == ModelCategory.REASONING
    assert reasoner.capabilities.supports_thinking is True

    vision = registry.get_model("gemma3-4b")
    assert vision is not None
    assert vision.type == ModelCategory.VISION
    assert vision.capabilities.supports_vision is True


def test_registry_filters_by_category():
    registry = get_model_registry()
    coding_models = registry.list_models(category=ModelCategory.CODING)
    assert len(coding_models) >= 1
    assert all(m.type == ModelCategory.CODING for m in coding_models)

    vision_models = registry.list_models(category=ModelCategory.VISION)
    assert len(vision_models) >= 1
    assert all(m.type == ModelCategory.VISION for m in vision_models)


def test_registry_dynamic_model_addition():
    registry = ModelRegistry()
    assert len(registry.list_models()) == 0

    custom_model = ModelMetadata(
        id="custom-fine-tuned-qwen",
        name="Custom Fine-Tuned Model",
        type=ModelCategory.CODING,
        provider="ollama",
        endpoint="http://127.0.0.1:11434",
        tag="custom-qwen:latest",
        capabilities=ModelCapabilitiesInfo(
            supports_vision=False,
            supports_tools=True,
            context_window=16384
        ),
        description="Dynamically registered without modifying router or tools."
    )

    registry.register_model(custom_model)
    retrieved = registry.get_model("custom-fine-tuned-qwen")
    assert retrieved is not None
    assert retrieved.name == "Custom Fine-Tuned Model"
    assert retrieved.capabilities.context_window == 16384


def test_registry_rejects_missing_file():
    with pytest.raises(RegistryConfigError) as exc_info:
        ModelRegistry(config_path="nonexistent_config_file_path_xyz.yaml")
    assert "not found" in str(exc_info.value).lower()


def test_registry_rejects_malformed_config_data():
    registry = ModelRegistry()
    # Malformed data: missing 'models' list
    with pytest.raises(RegistryConfigError) as exc_info:
        registry.load_from_dict({"version": "1.0", "invalid_key": []})
    assert "must contain a 'models' list" in str(exc_info.value)

    # Malformed data: invalid model entry missing required fields
    with pytest.raises(RegistryConfigError) as exc_info2:
        registry.load_from_dict({
            "models": [
                {"id": "incomplete-model"}  # missing name, type, tag, capabilities
            ]
        })
    assert "validation error" in str(exc_info2.value).lower()
