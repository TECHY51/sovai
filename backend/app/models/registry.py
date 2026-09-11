import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ValidationError


class ModelCategory(str, Enum):
    CODING = "coding"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDING = "embedding"


class ModelStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNVERIFIED = "unverified"


class RegistryConfigError(Exception):
    pass


class ModelCapabilitiesInfo(BaseModel):
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = True
    supports_thinking: bool = False
    context_window: int = 4096
    parameter_size: Optional[str] = None
    quantization: Optional[str] = None


class ModelMetadata(BaseModel):
    id: str
    name: str
    type: ModelCategory
    provider: str = "ollama"
    endpoint: str = "http://127.0.0.1:11434"
    tag: str
    capabilities: ModelCapabilitiesInfo
    description: str = ""
    status: ModelStatus = ModelStatus.UNVERIFIED


class ModelRegistry:
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self._models: Dict[str, ModelMetadata] = {}
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, path: Union[str, Path]) -> None:
        p = Path(path)
        if not p.is_file():
            raise RegistryConfigError(f"Registry configuration file not found at: {p}")
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise RegistryConfigError("Registry configuration must be a valid mapping.")
            self.load_from_dict(data)
        except yaml.YAMLError as exc:
            raise RegistryConfigError(f"YAML parsing error: {exc}")

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        raw_models = data.get("models")
        if not isinstance(raw_models, list):
            raise RegistryConfigError("Registry configuration must contain a 'models' list.")
        
        parsed_models: Dict[str, ModelMetadata] = {}
        for entry in raw_models:
            try:
                model = ModelMetadata(**entry)
                parsed_models[model.id] = model
            except ValidationError as exc:
                raise RegistryConfigError(f"Model validation error for '{entry}': {exc}")
        
        self._models = parsed_models

    def register_model(self, metadata: ModelMetadata) -> None:
        self._models[metadata.id] = metadata

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        return self._models.get(model_id)

    def list_models(
        self,
        category: Optional[ModelCategory] = None,
        available_only: bool = False
    ) -> List[ModelMetadata]:
        results = list(self._models.values())
        if category:
            results = [m for m in results if m.type == category]
        if available_only:
            results = [m for m in results if m.status == ModelStatus.AVAILABLE]
        return results

    def get_available_models(self) -> List[ModelMetadata]:
        return [m for m in self._models.values() if m.status == ModelStatus.AVAILABLE]

    def get_unavailable_models(self) -> List[ModelMetadata]:
        return [m for m in self._models.values() if m.status == ModelStatus.UNAVAILABLE]

    async def sync_availability(self, provider) -> None:
        health = await provider.health()
        installed = set(health.installed_models) if health.reachable else set()

        for model in self._models.values():
            if not health.reachable:
                model.status = ModelStatus.UNAVAILABLE
            elif model.tag in installed:
                model.status = ModelStatus.AVAILABLE
            else:
                model.status = ModelStatus.UNAVAILABLE
