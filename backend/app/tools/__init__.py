from typing import Optional
from backend.app.tools.tool_schema import (
    ToolDefinition,
    ToolParameter,
    ToolRiskLevel,
    PermissionLevel,
    PermissionContext,
    ToolExecutionRequest,
    ToolExecutionResult
)
from backend.app.tools.tool_registry import ToolRegistry, safe_calculate

_tool_registry_instance: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance


__all__ = [
    "ToolDefinition",
    "ToolParameter",
    "ToolRiskLevel",
    "PermissionLevel",
    "PermissionContext",
    "ToolExecutionRequest",
    "ToolExecutionResult",
    "ToolRegistry",
    "safe_calculate",
    "get_tool_registry"
]
