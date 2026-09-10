from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.models import get_model_provider, ProviderHealth, ModelCapabilities, ModelResponse, ModelError

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelTestRequest(BaseModel):
    model: str
    prompt: str = "Synthesize a concise Python hello world function."
    system: Optional[str] = "You are a precise industrial AI assistant."


@router.get("/health", response_model=ProviderHealth)
async def get_models_health() -> ProviderHealth:
    provider = get_model_provider()
    return await provider.health()


@router.get("/capabilities/{model:path}", response_model=ModelCapabilities)
async def get_model_capabilities(model: str) -> ModelCapabilities:
    provider = get_model_provider()
    try:
        return await provider.capabilities(model)
    except ModelError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/test", response_model=ModelResponse)
async def test_model_inference(request: ModelTestRequest) -> ModelResponse:
    provider = get_model_provider()
    try:
        return await provider.generate(
            model=request.model,
            prompt=request.prompt,
            system=request.system
        )
    except ModelError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
