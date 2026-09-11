import pytest
import json
from pathlib import Path
from backend.app.tools.tool_schema import (
    ToolDefinition,
    ToolRiskLevel,
    PermissionLevel,
    PermissionContext,
    ToolExecutionRequest
)
from backend.app.tools.tool_registry import ToolRegistry


@pytest.fixture
def clean_registry(tmp_path):
    ws = tmp_path / "test_workspace"
    audit_log = tmp_path / "test_audit.jsonl"
    return ToolRegistry(workspace_root=ws, audit_log_path=str(audit_log)), ws, audit_log


def test_every_enabled_tool_is_registered_centrally(clean_registry):
    registry, _, _ = clean_registry
    tools = registry.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "read_file",
        "write_file",
        "list_files",
        "search_documents",
        "run_python",
        "calculate",
        "ocr_document",
        "analyze_image",
        "create_docx",
        "create_xlsx",
        "create_pptx",
    }

    assert expected_tools.issubset(tool_names)
    assert all(t.enabled for t in tools)


def test_every_tool_has_machine_readable_schema(clean_registry):
    registry, _, _ = clean_registry
    for tool in registry.list_tools():
        schema = tool.to_json_schema()
        assert schema["type"] == "function"
        assert "function" in schema
        assert schema["function"]["name"] == tool.name
        assert "parameters" in schema["function"]
        assert schema["function"]["parameters"]["type"] == "object"
        assert "properties" in schema["function"]["parameters"]


def test_invalid_arguments_are_rejected_before_execution(clean_registry):
    registry, _, _ = clean_registry

    # Missing required argument 'expression'
    res1 = registry.execute_tool(ToolExecutionRequest(tool_name="calculate", arguments={}))
    assert res1.success is False
    assert "missing required argument" in res1.error.lower()

    # Wrong argument type for 'expression' (integer instead of string)
    res2 = registry.execute_tool(ToolExecutionRequest(tool_name="calculate", arguments={"expression": 12345}))
    assert res2.success is False
    assert "type string" in res2.error.lower()


def test_tool_permissions_checked_before_execution(clean_registry):
    registry, _, _ = clean_registry

    # Restrict permissions to read_only only
    read_only_ctx = PermissionContext(
        granted_permissions=[PermissionLevel.READ_ONLY.value],
        max_risk_level=ToolRiskLevel.LOW
    )

    # Attempt to execute write_file (requires workspace_write)
    res = registry.execute_tool(ToolExecutionRequest(
        tool_name="write_file",
        arguments={"path": "test.txt", "content": "hello"},
        permission_context=read_only_ctx
    ))
    assert res.success is False
    assert "permission denied" in res.error.lower()
    assert "workspace_write" in res.error.lower()


def test_risk_level_policy_enforcement(clean_registry):
    registry, _, _ = clean_registry

    # Allow up to MEDIUM risk
    low_risk_ctx = PermissionContext(
        granted_permissions=[
            PermissionLevel.READ_ONLY.value,
            PermissionLevel.WORKSPACE_WRITE.value,
            PermissionLevel.CODE_EXECUTION.value
        ],
        max_risk_level=ToolRiskLevel.MEDIUM
    )

    # run_python is HIGH risk -> must be blocked
    res = registry.execute_tool(ToolExecutionRequest(
        tool_name="run_python",
        arguments={"code": "x = 1"},
        permission_context=low_risk_ctx
    ))
    assert res.success is False
    assert "risk policy violation" in res.error.lower()


def test_agent_can_discover_only_allowlisted_tools(clean_registry):
    registry, _, _ = clean_registry
    allowlist = ["calculate", "read_file"]
    discovered = registry.get_allowlisted_tools(allowlist=allowlist)

    assert len(discovered) == 2
    discovered_names = {t.name for t in discovered}
    assert discovered_names == {"calculate", "read_file"}


def test_unknown_tools_cannot_be_executed(clean_registry):
    registry, _, _ = clean_registry
    res = registry.execute_tool(ToolExecutionRequest(
        tool_name="delete_production_database",
        arguments={"force": True}
    ))
    assert res.success is False
    assert "unknown tool" in res.error.lower()


def test_filesystem_tools_enforce_path_boundaries(clean_registry):
    registry, _, _ = clean_registry

    # Directory traversal attack attempt
    res_escape = registry.execute_tool(ToolExecutionRequest(
        tool_name="write_file",
        arguments={"path": "../../escaped_secret.txt", "content": "malicious"}
    ))
    assert res_escape.success is False
    assert "escape workspace boundary" in res_escape.error.lower()

    # Read escape attempt
    res_read_escape = registry.execute_tool(ToolExecutionRequest(
        tool_name="read_file",
        arguments={"path": "../../../system_config.ini"}
    ))
    assert res_read_escape.success is False
    assert "escape workspace boundary" in res_read_escape.error.lower()


def test_tool_executions_are_logged_to_audit_trail(clean_registry):
    registry, _, audit_log = clean_registry

    res = registry.execute_tool(ToolExecutionRequest(
        tool_name="calculate",
        arguments={"expression": "25 * 4"}
    ))
    assert res.success is True
    assert res.output == 100.0

    # Verify audit file was populated
    assert audit_log.is_file()
    lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    last_entry = json.loads(lines[-1])
    assert last_entry["tool_name"] == "calculate"
    assert last_entry["success"] is True
    assert "duration_ms" in last_entry
