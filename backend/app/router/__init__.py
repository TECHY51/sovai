from typing import Optional
from backend.app.router.router_schema import TaskType, RoutingRequest, RoutingDecision
from backend.app.router.task_router import TaskRouter

_router_instance: Optional[TaskRouter] = None


def get_task_router() -> TaskRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = TaskRouter()
    return _router_instance


__all__ = [
    "TaskRouter",
    "TaskType",
    "RoutingRequest",
    "RoutingDecision",
    "get_task_router"
]
