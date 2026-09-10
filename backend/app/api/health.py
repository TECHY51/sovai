from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from backend.app.core.config import settings
from backend.app.models import get_model_provider

router = APIRouter(prefix="/api", tags=["health"])


class SubsystemStatus(BaseModel):
    status: str
    phase: int
    description: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str
    airgap_mode: bool
    subsystems: Dict[str, SubsystemStatus]


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    provider = get_model_provider()
    provider_health = await provider.health()
    
    model_infra_status = "READY" if provider_health.reachable else "UNAVAILABLE"
    model_infra_desc = (
        f"Local model provider active at {provider_health.endpoint} with {len(provider_health.installed_models)} models."
        if provider_health.reachable
        else f"Local model provider unreachable at {provider_health.endpoint}: {provider_health.error_message}"
    )

    subsystem_states = {
        "api_backend": SubsystemStatus(
            status="READY",
            phase=0,
            description="Core FastAPI application and routing skeleton active."
        ),
        "model_infrastructure": SubsystemStatus(
            status=model_infra_status,
            phase=1,
            description=model_infra_desc
        ),
        "model_registry": SubsystemStatus(
            status="PENDING",
            phase=2,
            description="Model registry scheduled for Phase 2."
        ),
        "task_router": SubsystemStatus(
            status="PENDING",
            phase=3,
            description="Task-to-model router scheduled for Phase 3."
        ),
        "agent_orchestrator": SubsystemStatus(
            status="PENDING",
            phase=4,
            description="Stateful agent loop scheduled for Phase 4."
        ),
        "tool_registry": SubsystemStatus(
            status="PENDING",
            phase=5,
            description="Tool registry and execution layer scheduled for Phase 5."
        ),
        "sandbox": SubsystemStatus(
            status="PENDING",
            phase=6,
            description="Python execution sandbox scheduled for Phase 6."
        ),
        "knowledge_base": SubsystemStatus(
            status="PENDING",
            phase=7,
            description="Local RAG vector store scheduled for Phase 7."
        ),
        "multimodal": SubsystemStatus(
            status="PENDING",
            phase=8,
            description="OCR and vision pipeline scheduled for Phase 8."
        ),
        "artifact_generator": SubsystemStatus(
            status="PENDING",
            phase=9,
            description="DOCX/XLSX/PPTX generators scheduled for Phase 9."
        ),
        "verification_engine": SubsystemStatus(
            status="PENDING",
            phase=10,
            description="Verification engine scheduled for Phase 10."
        ),
        "security_layer": SubsystemStatus(
            status="READY",
            phase=12,
            description="Air-gap enforcement and audit logging boundaries active."
        )
    }

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.SOVAI_VERSION,
        environment=settings.SOVAI_ENV,
        airgap_mode=settings.SOVAI_STRICT_AIRGAP_MODE,
        subsystems=subsystem_states
    )
