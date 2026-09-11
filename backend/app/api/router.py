from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.app.router import (
    get_task_router,
    RoutingRequest,
    RoutingDecision,
    TaskType
)
from backend.app.router.task_router import PREFERRED_MODELS, DEFAULT_TOOLS
from backend.app.models import get_model_provider, get_model_registry

router = APIRouter(prefix="/api/router", tags=["router"])


@router.post("/route", response_model=RoutingDecision)
async def route_task(
    request: RoutingRequest,
    sync: bool = Query(False, description="Synchronize availability with live provider before routing")
) -> RoutingDecision:
    if sync:
        provider = get_model_provider()
        registry = get_model_registry()
        await registry.sync_availability(provider)
    task_router = get_task_router()
    return task_router.route(request)


@router.get("/history", response_model=List[RoutingDecision])
async def get_routing_history() -> List[RoutingDecision]:
    task_router = get_task_router()
    return task_router.get_history()


@router.get("/mappings")
async def get_router_mappings() -> Dict[str, Any]:
    return {
        "preferred_models": {k.value: v for k, v in PREFERRED_MODELS.items()},
        "default_tools": {k.value: v for k, v in DEFAULT_TOOLS.items()}
    }
