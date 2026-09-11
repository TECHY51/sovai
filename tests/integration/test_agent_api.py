import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_run_agent_multistep_workflow():
    payload = {
        "prompt": "Calculate structural tension: compute 450 * 2.5 and save report to audit file."
    }
    response = client.post("/api/agent/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["task_id"] is not None
    assert len(data["plan"]) >= 2
    assert len(data["trace"]) >= 5
    assert data["final_response"] is not None
    assert data["routed_model"] is not None

    # Step tools check
    tools_used = [s["tool_name"] for s in data["plan"] if s.get("tool_name")]
    assert "calculate" in tools_used
    assert "write_file" in tools_used or "read_file" in tools_used


def test_api_get_agent_tasks_and_task_by_id():
    # Execute a run first
    run_res = client.post("/api/agent/run", json={"prompt": "Write log message to file"})
    assert run_res.status_code == 200
    task_id = run_res.json()["task_id"]

    # List tasks
    list_res = client.get("/api/agent/tasks")
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert any(t["task_id"] == task_id for t in tasks)

    # Get single task
    single_res = client.get(f"/api/agent/tasks/{task_id}")
    assert single_res.status_code == 200
    single_task = single_res.json()
    assert single_task["task_id"] == task_id
    assert single_task["status"] == "completed"


def test_api_get_task_trace():
    run_res = client.post("/api/agent/run", json={"prompt": "Calculate 80 + 20"})
    assert run_res.status_code == 200
    task_id = run_res.json()["task_id"]

    trace_res = client.get(f"/api/agent/tasks/{task_id}/trace")
    assert trace_res.status_code == 200
    trace = trace_res.json()
    assert isinstance(trace, list)
    assert len(trace) >= 4
    stages = [t["stage"] for t in trace]
    assert "understand" in stages
    assert "route" in stages
    assert "act" in stages
    assert "deliver" in stages


def test_api_get_nonexistent_task_returns_404():
    res = client.get("/api/agent/tasks/unknown-task-99999")
    assert res.status_code == 404
    assert "detail" in res.json()


def test_health_reports_agent_orchestrator_ready():
    response = client.get("/api/health")
    assert response.status_code == 200
    subsystems = response.json()["subsystems"]
    assert "agent_orchestrator" in subsystems
    assert subsystems["agent_orchestrator"]["status"] == "READY"
    assert subsystems["agent_orchestrator"]["phase"] == 4
