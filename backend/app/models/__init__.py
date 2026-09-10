from backend.app.core.config import settings
from backend.app.models.base import (
    ModelProvider,
    ModelResponse,
    ProviderHealth,
    ModelCapabilities,
    ModelError
)
from backend.app.models.ollama import OllamaProvider

_default_provider: ModelProvider = None


def get_model_provider() -> ModelProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = OllamaProvider(
            endpoint=settings.SOVAI_INFERENCE_ENDPOINT,
            timeout_seconds=float(settings.SOVAI_INFERENCE_TIMEOUT_SECONDS)
        )
    return _default_provider


__all__ = [
    "ModelProvider",
    "OllamaProvider",
    "ModelResponse",
    "ProviderHealth",
    "ModelCapabilities",
    "ModelError",
    "get_model_provider"
]
