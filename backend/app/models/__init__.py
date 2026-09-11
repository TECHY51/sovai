from pathlib import Path
from backend.app.core.config import settings
from backend.app.models.base import (
    ModelProvider,
    ModelResponse,
    ProviderHealth,
    ModelCapabilities,
    ModelError
)
from backend.app.models.ollama import OllamaProvider
from backend.app.models.registry import (
    ModelRegistry,
    ModelMetadata,
    ModelCategory,
    ModelStatus,
    RegistryConfigError
)

_default_provider: ModelProvider = None
_default_registry: ModelRegistry = None


def get_model_provider() -> ModelProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = OllamaProvider(
            endpoint=settings.SOVAI_INFERENCE_ENDPOINT,
            timeout_seconds=float(settings.SOVAI_INFERENCE_TIMEOUT_SECONDS)
        )
    return _default_provider


def get_model_registry() -> ModelRegistry:
    global _default_registry
    if _default_registry is None:
        # Resolve path relative to project root
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        config_path = root_dir / "models" / "registry.yaml"
        _default_registry = ModelRegistry(config_path=config_path if config_path.exists() else None)
    return _default_registry


__all__ = [
    "ModelProvider",
    "OllamaProvider",
    "ModelResponse",
    "ProviderHealth",
    "ModelCapabilities",
    "ModelError",
    "ModelRegistry",
    "ModelMetadata",
    "ModelCategory",
    "ModelStatus",
    "RegistryConfigError",
    "get_model_provider",
    "get_model_registry"
]
