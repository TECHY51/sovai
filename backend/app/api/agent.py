from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.agent import (
    get_agent_orchestrator,
    AgentRunRequest,
    AgentState,
    TraceEvent
)

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/run", response_model=AgentState)
async def run_agent_workflow(request: AgentRunRequest) -> AgentState:
    orchestrator = get_agent_orchestrator()
    return orchestrator.run_task(prompt=request.prompt, task_id=request.task_id)


@router.get("/tasks", response_model=List[AgentState])
async def list_agent_tasks() -> List[AgentState]:
    orchestrator = get_agent_orchestrator()
    return orchestrator.list_tasks()


@router.get("/tasks/{task_id}", response_model=AgentState)
async def get_agent_task(task_id: str) -> AgentState:
    orchestrator = get_agent_orchestrator()
    task = orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")
    return task


@router.get("/tasks/{task_id}/trace", response_model=List[TraceEvent])
async def get_task_trace(task_id: str) -> List[TraceEvent]:
    orchestrator = get_agent_orchestrator()
    task = orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID '{task_id}' not found.")
    return task.trace
