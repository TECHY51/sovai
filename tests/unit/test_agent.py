import pytest
from pathlib import Path
from backend.app.agent.agent_schema import AgentState, TaskStatus
from backend.app.agent.agent_orchestrator import AgentOrchestrator
from backend.app.tools.tool_registry import ToolRegistry
from backend.app.router.task_router import TaskRouter
from backend.app.models.registry import (
    ModelRegistry,
    ModelMetadata,
    ModelCategory,
    ModelStatus,
    ModelCapabilitiesInfo
)


@pytest.fixture
def test_env(tmp_path):
    # Mock registry with available models
    registry = ModelRegistry()
    registry.register_model(ModelMetadata(
        id="qwen2.5-coder-3b",
        name="Qwen2.5-Coder-3B",
        type=ModelCategory.CODING,
        tag="qwen2.5-coder:3b",
        capabilities=ModelCapabilitiesInfo(supports_tools=True),
        status=ModelStatus.AVAILABLE
    ))
    registry.register_model(ModelMetadata(
        id="qwen3-4b",
        name="Qwen3-4B",
        type=ModelCategory.REASONING,
        tag="qwen3:4b",
        capabilities=ModelCapabilitiesInfo(supports_tools=True, supports_thinking=True),
        status=ModelStatus.AVAILABLE
    ))

    router = TaskRouter(registry=registry, audit_log_path=None)
    tools = ToolRegistry(workspace_root=tmp_path / "agent_ws")
    orchestrator = AgentOrchestrator(router=router, tools=tools)
    return orchestrator, tools


def test_agent_maintains_explicit_task_state(test_env):
    orchestrator, _ = test_env
    prompt = "Perform safety calculation: compute (50 * 4) + 20 and record report"
    state = orchestrator.run_task(prompt=prompt)

    assert isinstance(state, AgentState)
    assert state.task_id is not None
    assert state.prompt == prompt
    assert state.status == TaskStatus.COMPLETED
    assert len(state.plan) >= 2
    assert len(state.trace) >= 4
    assert state.routed_model is not None


def test_agent_creates_and_executes_multistep_plan(test_env):
    orchestrator, _ = test_env
    prompt = "Compute engineering load formula: 120 * 5"
    state = orchestrator.run_task(prompt=prompt)

    assert state.status == TaskStatus.COMPLETED
    assert len(state.plan) >= 2
    for step in state.plan:
        assert step.status == "completed"
        assert step.result is not None


def test_agent_invokes_at_least_two_different_tools_in_single_workflow(test_env):
    orchestrator, _ = test_env
    prompt = "Calculate 250 / 5 and save to audit file"
    state = orchestrator.run_task(prompt=prompt)

    tools_used = {step.tool_name for step in state.plan if step.tool_name}
    assert len(tools_used) >= 2
    assert "calculate" in tools_used
    assert "write_file" in tools_used or "read_file" in tools_used


def test_tool_results_are_returned_to_agent(test_env):
    orchestrator, _ = test_env
    prompt = "Calculate 15 * 10"
    state = orchestrator.run_task(prompt=prompt)

    step_1 = state.plan[0]
    assert step_1.tool_name == "calculate"
    assert step_1.result == 150.0
    assert "step_1_result" in state.variables
    assert state.variables["step_1_result"] == 150.0


def test_agent_controlled_retry_on_failure(test_env):
    orchestrator, _ = test_env
    # Division by zero triggers a failure and a controlled retry
    prompt = "Calculate formula: 100 / 0"
    state = orchestrator.run_task(prompt=prompt)

    # Should have triggered retry
    assert state.retry_count >= 1
    # Verify iteration event exists in trace
    iterate_events = [e for e in state.trace if e.stage == "iterate"]
    assert len(iterate_events) >= 1
    assert "controlled retry" in iterate_events[0].action.lower()


def test_agent_execution_trace_records_major_steps(test_env):
    orchestrator, _ = test_env
    state = orchestrator.run_task(prompt="Write log entry to file and verify")

    stages_in_trace = {e.stage for e in state.trace}
    expected_stages = {"understand", "route", "plan", "act", "observe", "verify", "deliver"}
    assert expected_stages.issubset(stages_in_trace)


def test_agent_persists_and_retrieves_tasks(test_env):
    orchestrator, _ = test_env
    state = orchestrator.run_task(prompt="Calculate 50 + 50")
    retrieved = orchestrator.get_task(state.task_id)

    assert retrieved is not None
    assert retrieved.task_id == state.task_id
    assert retrieved.status == TaskStatus.COMPLETED
