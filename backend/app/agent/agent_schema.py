import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    CREATED = "created"
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    ROUTING = "routing"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    ITERATING = "iterating"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStep(BaseModel):
    step_number: int
    description: str
    action_type: str = "tool_call"  # "tool_call" | "model_reasoning" | "verification"
    tool_name: Optional[str] = None
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # "pending" | "executing" | "completed" | "failed" | "retried"
    result: Optional[Any] = None
    error: Optional[str] = None


class TraceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    stage: str  # "understand" | "plan" | "route" | "act" | "observe" | "verify" | "iterate" | "deliver"
    step_number: Optional[int] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentState(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    status: TaskStatus = TaskStatus.CREATED
    routed_model: Optional[str] = None
    plan: List[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    trace: List[TraceEvent] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    variables: Dict[str, Any] = Field(default_factory=dict)
    final_response: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentRunRequest(BaseModel):
    prompt: str
    task_id: Optional[str] = None
    max_steps: int = 10
    context: Optional[Dict[str, Any]] = None
