import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_list_tools_and_allowlist_filtering():
    # List all
    res = client.get("/api/tools")
    assert res.status_code == 200
    tools = res.json()
    assert len(tools) >= 11
    names = {t["name"] for t in tools}
    assert "calculate" in names
    assert "write_file" in names

    # Filter allowlist
    filter_res = client.get("/api/tools?allowlist=calculate,read_file")
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert len(filtered) == 2
    assert {t["name"] for t in filtered} == {"calculate", "read_file"}


def test_api_get_tool_schemas():
    res = client.get("/api/tools/schemas")
    assert res.status_code == 200
    schemas = res.json()
    assert len(schemas) >= 11
    for s in schemas:
        assert s["type"] == "function"
        assert "function" in s
        assert "parameters" in s["function"]


def test_api_get_tool_permissions():
    res = client.get("/api/tools/permissions")
    assert res.status_code == 200
    data = res.json()
    assert "read_only" in data["permission_levels"]
    assert "workspace_write" in data["permission_levels"]
    assert "low" in data["risk_levels"]


def test_api_get_single_tool_and_404_for_unknown():
    res = client.get("/api/tools/calculate")
    assert res.status_code == 200
    assert res.json()["name"] == "calculate"

    res_unknown = client.get("/api/tools/nonexistent_tool_xyz")
    assert res_unknown.status_code == 404


def test_api_execute_tool_success_and_permission_denial():
    # Valid execution
    valid_res = client.post("/api/tools/execute", json={
        "tool_name": "calculate",
        "arguments": {"expression": "(40 * 2.5) + 10"}
    })
    assert valid_res.status_code == 200
    data = valid_res.json()
    assert data["success"] is True
    assert data["output"] == 110.0

    # Permission denial execution
    denied_res = client.post("/api/tools/execute", json={
        "tool_name": "write_file",
        "arguments": {"path": "blocked.txt", "content": "blocked content"},
        "permission_context": {
            "granted_permissions": ["read_only"],
            "max_risk_level": "low"
        }
    })
    assert denied_res.status_code == 200
    denied_data = denied_res.json()
    assert denied_data["success"] is False
    assert "permission denied" in denied_data["error"].lower()


def test_api_execute_unknown_tool_returns_404():
    res = client.post("/api/tools/execute", json={
        "tool_name": "unauthorized_admin_tool",
        "arguments": {}
    })
    assert res.status_code == 404


def test_health_reports_tool_registry_ready():
    response = client.get("/api/health")
    assert response.status_code == 200
    subsystems = response.json()["subsystems"]
    assert "tool_registry" in subsystems
    assert subsystems["tool_registry"]["status"] == "READY"
    assert subsystems["tool_registry"]["phase"] == 5
