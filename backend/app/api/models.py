from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.models import (
    get_model_provider,
    get_model_registry,
    ProviderHealth,
    ModelCapabilities,
    ModelResponse,
    ModelError,
    ModelMetadata,
    ModelCategory
)

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


@router.get("/registry", response_model=List[ModelMetadata])
async def list_registry_models(
    category: Optional[ModelCategory] = Query(None, description="Filter by category"),
    available_only: bool = Query(False, description="Filter to only currently available models"),
    sync: bool = Query(True, description="Synchronize availability with active provider")
) -> List[ModelMetadata]:
    registry = get_model_registry()
    if sync:
        provider = get_model_provider()
        await registry.sync_availability(provider)
    return registry.list_models(category=category, available_only=available_only)


@router.get("/registry/{model_id}", response_model=ModelMetadata)
async def get_registry_model(
    model_id: str,
    sync: bool = Query(True, description="Synchronize availability with active provider")
) -> ModelMetadata:
    registry = get_model_registry()
    if sync:
        provider = get_model_provider()
        await registry.sync_availability(provider)
    model = registry.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry.")
    return model


@router.post("/registry/sync")
async def sync_registry():
    registry = get_model_registry()
    provider = get_model_provider()
    await registry.sync_availability(provider)
    available = registry.get_available_models()
    unavailable = registry.get_unavailable_models()
    return {
        "status": "synchronized",
        "total_registered": len(registry.list_models()),
        "available_count": len(available),
        "unavailable_count": len(unavailable),
        "available_ids": [m.id for m in available],
        "unavailable_ids": [m.id for m in unavailable]
    }
