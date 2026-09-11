from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    CODING = "coding"
    REASONING = "reasoning"
    VISION = "vision"
    GENERAL = "general"
    AMBIGUOUS = "ambiguous"


class RoutingRequest(BaseModel):
    prompt: str = Field(..., description="User query or task prompt to be analyzed and routed")
    task_type_hint: Optional[TaskType] = Field(None, description="Explicit operator hint if provided")
    files: Optional[List[str]] = Field(default=None, description="Optional attached filenames, extensions, or URIs")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Arbitrary execution context metadata")


class RoutingDecision(BaseModel):
    task_type: TaskType
    model_id: str
    model_tag: str
    tools: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    fallback_used: bool = False
    clarification_needed: bool = False
    clarification_prompt: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
