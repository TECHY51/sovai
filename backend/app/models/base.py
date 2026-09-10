from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncIterator
from pydantic import BaseModel, Field


class ModelCapabilities(BaseModel):
    model: str
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = True
    context_window: int = 4096
    verified: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    model: str
    content: str
    thinking: Optional[str] = None
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    latency_ms: float = 0.0
    done: bool = True


class ProviderHealth(BaseModel):
    provider: str
    endpoint: str
    reachable: bool
    latency_ms: float = 0.0
    installed_models: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class ModelError(Exception):
    def __init__(self, message: str, status_code: int = 500, model: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.model = model


class ModelProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        images: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        pass

    @abstractmethod
    async def stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        images: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def health(self) -> ProviderHealth:
        pass

    @abstractmethod
    async def capabilities(self, model: str) -> ModelCapabilities:
        pass
