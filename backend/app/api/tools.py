from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.app.tools import (
    get_tool_registry,
    ToolDefinition,
    ToolExecutionRequest,
    ToolExecutionResult,
    PermissionLevel,
    ToolRiskLevel
)

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("", response_model=List[ToolDefinition])
async def list_tools(
    allowlist: Optional[str] = Query(None, description="Comma-separated tool allowlist filter")
) -> List[ToolDefinition]:
    registry = get_tool_registry()
    allowed = [t.strip() for t in allowlist.split(",")] if allowlist else None
    return registry.get_allowlisted_tools(allowed)


@router.get("/schemas")
async def list_tool_schemas(
    allowlist: Optional[str] = Query(None, description="Comma-separated tool allowlist filter")
) -> List[Dict[str, Any]]:
    registry = get_tool_registry()
    allowed = [t.strip() for t in allowlist.split(",")] if allowlist else None
    tools = registry.get_allowlisted_tools(allowed)
    return [t.to_json_schema() for t in tools]


@router.get("/permissions")
async def get_tool_permissions() -> Dict[str, Any]:
    return {
        "permission_levels": [p.value for p in PermissionLevel],
        "risk_levels": [r.value for r in ToolRiskLevel]
    }


@router.get("/{name}", response_model=ToolDefinition)
async def get_tool(name: str) -> ToolDefinition:
    registry = get_tool_registry()
    tool = registry.get_tool(name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found in registry.")
    return tool


@router.post("/execute", response_model=ToolExecutionResult)
async def execute_tool(request: ToolExecutionRequest) -> ToolExecutionResult:
    registry = get_tool_registry()
    result = registry.execute_tool(request)
    if not result.success and "Unknown tool" in (result.error or ""):
        raise HTTPException(status_code=404, detail=result.error)
    return result
