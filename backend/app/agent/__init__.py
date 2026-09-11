from typing import Optional
from backend.app.agent.agent_schema import (
    AgentState,
    TaskStatus,
    PlanStep,
    TraceEvent,
    AgentRunRequest
)
from backend.app.agent.agent_orchestrator import AgentOrchestrator

_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_agent_orchestrator() -> AgentOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance


__all__ = [
    "AgentState",
    "TaskStatus",
    "PlanStep",
    "TraceEvent",
    "AgentRunRequest",
    "AgentOrchestrator",
    "get_agent_orchestrator"
]
