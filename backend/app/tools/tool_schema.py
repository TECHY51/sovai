from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionLevel(str, Enum):
    READ_ONLY = "read_only"
    WORKSPACE_WRITE = "workspace_write"
    CODE_EXECUTION = "code_execution"
    MULTIMODAL = "multimodal"
    DOCUMENT_GENERATION = "document_generation"
    ADMIN = "admin"


class ToolParameter(BaseModel):
    name: str
    type: str  # "string", "number", "integer", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    permission: str = PermissionLevel.READ_ONLY.value
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    enabled: bool = True

    def to_json_schema(self) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        required: List[str] = []
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            },
            "permission": self.permission,
            "risk_level": self.risk_level.value,
            "enabled": self.enabled
        }


class PermissionContext(BaseModel):
    granted_permissions: List[str] = Field(
        default_factory=lambda: [
            PermissionLevel.READ_ONLY.value,
            PermissionLevel.WORKSPACE_WRITE.value,
            PermissionLevel.CODE_EXECUTION.value,
            PermissionLevel.MULTIMODAL.value,
            PermissionLevel.DOCUMENT_GENERATION.value
        ]
    )
    max_risk_level: ToolRiskLevel = ToolRiskLevel.HIGH
    allowlist: Optional[List[str]] = None


class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    permission_context: Optional[PermissionContext] = None


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    risk_level: Optional[ToolRiskLevel] = None
