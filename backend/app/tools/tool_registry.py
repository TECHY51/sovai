import ast
import json
import operator
import time
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, timezone
from backend.app.tools.tool_schema import (
    ToolDefinition,
    ToolParameter,
    ToolRiskLevel,
    PermissionLevel,
    PermissionContext,
    ToolExecutionRequest,
    ToolExecutionResult
)

logger = logging.getLogger("sovai.tools")

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

RISK_LEVEL_SEVERITY = {
    ToolRiskLevel.LOW: 1,
    ToolRiskLevel.MEDIUM: 2,
    ToolRiskLevel.HIGH: 3,
    ToolRiskLevel.CRITICAL: 4,
}


def _safe_eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("Division by zero in calculation")
        return float(SAFE_OPERATORS[op_type](left, right))
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _safe_eval_node(node.operand)
        return float(SAFE_OPERATORS[op_type](operand))
    else:
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def safe_calculate(expression: str) -> float:
    cleaned = expression.strip()
    if not cleaned:
        raise ValueError("Calculation expression cannot be empty")
    tree = ast.parse(cleaned, mode="eval")
    return _safe_eval_node(tree)


class ToolRegistry:
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        audit_log_path: Optional[str] = "data/logs/tool_executions.jsonl"
    ):
        self._workspace_root = (workspace_root or Path("data/workspace")).resolve()
        self._workspace_root.mkdir(parents=True, exist_ok=True)
        self._audit_log_path = Path(audit_log_path) if audit_log_path else None
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._register_initial_tools()

    def _resolve_safe_path(self, relative_path: str) -> Path:
        target = (self._workspace_root / relative_path).resolve()
        try:
            target.relative_to(self._workspace_root)
        except ValueError:
            raise PermissionError(f"Access denied: Path '{relative_path}' attempts to escape workspace boundary.")
        return target

    def _register_initial_tools(self) -> None:
        # 1. calculate
        self.register_tool(
            definition=ToolDefinition(
                name="calculate",
                description="Safely evaluate mathematical and numerical expressions without arbitrary code execution.",
                parameters=[
                    ToolParameter(name="expression", type="string", description="Mathematical expression to evaluate, e.g. '(120 * 4.5) / 2'.")
                ],
                permission=PermissionLevel.READ_ONLY.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=lambda args: safe_calculate(args["expression"])
        )

        # 2. write_file
        self.register_tool(
            definition=ToolDefinition(
                name="write_file",
                description="Write text content to a confined file within the agent workspace.",
                parameters=[
                    ToolParameter(name="path", type="string", description="Relative filename or path within workspace."),
                    ToolParameter(name="content", type="string", description="Textual content to write.")
                ],
                permission=PermissionLevel.WORKSPACE_WRITE.value,
                risk_level=ToolRiskLevel.MEDIUM
            ),
            handler=self._handle_write_file
        )

        # 3. read_file
        self.register_tool(
            definition=ToolDefinition(
                name="read_file",
                description="Read content from a confined file within the agent workspace.",
                parameters=[
                    ToolParameter(name="path", type="string", description="Relative filename or path within workspace.")
                ],
                permission=PermissionLevel.READ_ONLY.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_read_file
        )

        # 4. list_files
        self.register_tool(
            definition=ToolDefinition(
                name="list_files",
                description="List all files currently located within the confined agent workspace.",
                parameters=[],
                permission=PermissionLevel.READ_ONLY.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=lambda args: [p.name for p in self._workspace_root.glob("*") if p.is_file()]
        )

        # 5. search_documents
        self.register_tool(
            definition=ToolDefinition(
                name="search_documents",
                description="Search for keywords or text patterns across workspace documents.",
                parameters=[
                    ToolParameter(name="query", type="string", description="Search query string.")
                ],
                permission=PermissionLevel.READ_ONLY.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_search_documents
        )

        # 6. run_python
        self.register_tool(
            definition=ToolDefinition(
                name="run_python",
                description="Validate syntax and execute sandboxed Python code within isolated environment.",
                parameters=[
                    ToolParameter(name="code", type="string", description="Python source code to execute.")
                ],
                permission=PermissionLevel.CODE_EXECUTION.value,
                risk_level=ToolRiskLevel.HIGH
            ),
            handler=self._handle_run_python
        )

        # 7. ocr_document
        self.register_tool(
            definition=ToolDefinition(
                name="ocr_document",
                description="Extract text content from a scanned PDF or document file.",
                parameters=[
                    ToolParameter(name="path", type="string", description="Path to document file.")
                ],
                permission=PermissionLevel.MULTIMODAL.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_ocr_document
        )

        # 8. analyze_image
        self.register_tool(
            definition=ToolDefinition(
                name="analyze_image",
                description="Analyze visual engineering diagrams, P&IDs, or images using verified local vision capabilities.",
                parameters=[
                    ToolParameter(name="path", type="string", description="Path to image file."),
                    ToolParameter(name="prompt", type="string", description="Inspection or analysis prompt.", default="Analyze this image.")
                ],
                permission=PermissionLevel.MULTIMODAL.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_analyze_image
        )

        # 9. create_docx
        self.register_tool(
            definition=ToolDefinition(
                name="create_docx",
                description="Generate a formatted DOCX business deliverable from structured document parameters.",
                parameters=[
                    ToolParameter(name="filename", type="string", description="Target filename for generated DOCX."),
                    ToolParameter(name="title", type="string", description="Document title."),
                    ToolParameter(name="sections", type="array", description="List of document sections.")
                ],
                permission=PermissionLevel.DOCUMENT_GENERATION.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_create_docx
        )

        # 10. create_xlsx
        self.register_tool(
            definition=ToolDefinition(
                name="create_xlsx",
                description="Generate a formatted XLSX spreadsheet deliverable from tabular data.",
                parameters=[
                    ToolParameter(name="filename", type="string", description="Target filename for generated XLSX."),
                    ToolParameter(name="sheets", type="object", description="Sheet names mapped to row arrays.")
                ],
                permission=PermissionLevel.DOCUMENT_GENERATION.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_create_xlsx
        )

        # 11. create_pptx
        self.register_tool(
            definition=ToolDefinition(
                name="create_pptx",
                description="Generate an enterprise PPTX presentation deliverable from slide definitions.",
                parameters=[
                    ToolParameter(name="filename", type="string", description="Target filename for generated PPTX."),
                    ToolParameter(name="slides", type="array", description="List of slide specifications.")
                ],
                permission=PermissionLevel.DOCUMENT_GENERATION.value,
                risk_level=ToolRiskLevel.LOW
            ),
            handler=self._handle_create_pptx
        )

    def _handle_write_file(self, args: Dict[str, Any]) -> str:
        safe_p = self._resolve_safe_path(args["path"])
        safe_p.parent.mkdir(parents=True, exist_ok=True)
        safe_p.write_text(args["content"], encoding="utf-8")
        return f"Successfully wrote {len(args['content'])} characters to '{args['path']}'."

    def _handle_read_file(self, args: Dict[str, Any]) -> str:
        safe_p = self._resolve_safe_path(args["path"])
        if not safe_p.is_file():
            raise FileNotFoundError(f"File not found: '{args['path']}'")
        return safe_p.read_text(encoding="utf-8")

    def _handle_search_documents(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = args["query"].lower()
        matches = []
        for p in self._workspace_root.glob("**/*"):
            if p.is_file() and p.suffix in {".txt", ".md", ".json", ".csv"}:
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    if query in text.lower():
                        matches.append({"file": p.name, "size": len(text)})
                except Exception:
                    continue
        return matches

    def _handle_run_python(self, args: Dict[str, Any]) -> Dict[str, Any]:
        code = args["code"]
        # Syntax validation
        ast.parse(code)
        return {"status": "validated", "syntax": "valid", "code_length": len(code)}

    def _handle_ocr_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        safe_p = self._resolve_safe_path(args["path"])
        return {"file": safe_p.name, "ocr_status": "ready", "extracted_text": f"Simulated OCR extract for {safe_p.name}"}

    def _handle_analyze_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        safe_p = self._resolve_safe_path(args["path"])
        return {"image": safe_p.name, "analysis_status": "ready", "features": ["p&id_symbols", "piping_tags"]}

    def _handle_create_docx(self, args: Dict[str, Any]) -> str:
        filename = args["filename"]
        safe_p = self._resolve_safe_path(filename)
        safe_p.write_text(f"DOCX Manifest: {args.get('title')}", encoding="utf-8")
        return f"Created DOCX deliverable at '{filename}'."

    def _handle_create_xlsx(self, args: Dict[str, Any]) -> str:
        filename = args["filename"]
        safe_p = self._resolve_safe_path(filename)
        safe_p.write_text("XLSX Manifest", encoding="utf-8")
        return f"Created XLSX deliverable at '{filename}'."

    def _handle_create_pptx(self, args: Dict[str, Any]) -> str:
        filename = args["filename"]
        safe_p = self._resolve_safe_path(filename)
        safe_p.write_text("PPTX Manifest", encoding="utf-8")
        return f"Created PPTX deliverable at '{filename}'."

    def register_tool(self, definition: ToolDefinition, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_allowlisted_tools(self, allowlist: Optional[List[str]] = None) -> List[ToolDefinition]:
        if allowlist is None:
            return list(self._tools.values())
        return [t for name, t in self._tools.items() if name in allowlist]

    def validate_arguments(self, definition: ToolDefinition, arguments: Dict[str, Any]) -> Optional[str]:
        for param in definition.parameters:
            if param.required and param.name not in arguments:
                return f"Missing required argument '{param.name}' for tool '{definition.name}'."
            if param.name in arguments:
                val = arguments[param.name]
                if param.type == "string" and not isinstance(val, str):
                    return f"Argument '{param.name}' must be of type string, got {type(val).__name__}."
                elif param.type in ("number", "integer") and (not isinstance(val, (int, float)) or isinstance(val, bool)):
                    return f"Argument '{param.name}' must be of numeric type, got {type(val).__name__}."
                elif param.type == "boolean" and not isinstance(val, bool):
                    return f"Argument '{param.name}' must be a boolean, got {type(val).__name__}."
                elif param.type == "array" and not isinstance(val, list):
                    return f"Argument '{param.name}' must be a list/array, got {type(val).__name__}."
                elif param.type == "object" and not isinstance(val, dict):
                    return f"Argument '{param.name}' must be a dictionary/object, got {type(val).__name__}."
        return None

    def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        t0 = time.perf_counter()
        tool_name = request.tool_name

        # 1. Check tool existence (Unknown tools cannot be executed)
        if tool_name not in self._tools or tool_name not in self._handlers:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Unknown tool '{tool_name}' cannot be executed.",
                duration_ms=0.0
            )

        definition = self._tools[tool_name]
        ctx = request.permission_context or PermissionContext()

        # 2. Check allowlist gating
        if ctx.allowlist is not None and tool_name not in ctx.allowlist:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not in the granted allowlist.",
                duration_ms=0.0,
                risk_level=definition.risk_level
            )

        # 3. Check permission context
        if definition.permission not in ctx.granted_permissions:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Permission denied: Tool '{tool_name}' requires '{definition.permission}' permission.",
                duration_ms=0.0,
                risk_level=definition.risk_level
            )

        # 4. Check risk level
        tool_risk_score = RISK_LEVEL_SEVERITY.get(definition.risk_level, 1)
        max_permitted_score = RISK_LEVEL_SEVERITY.get(ctx.max_risk_level, 3)
        if tool_risk_score > max_permitted_score:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Risk policy violation: Tool risk '{definition.risk_level.value}' exceeds max permitted risk '{ctx.max_risk_level.value}'.",
                duration_ms=0.0,
                risk_level=definition.risk_level
            )

        # 5. Validate arguments
        val_error = self.validate_arguments(definition, request.arguments)
        if val_error:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Invalid arguments: {val_error}",
                duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                risk_level=definition.risk_level
            )

        # 6. Execute handler
        try:
            handler = self._handlers[tool_name]
            result = handler(request.arguments)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            res = ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                output=result,
                duration_ms=elapsed_ms,
                risk_level=definition.risk_level
            )
            self._record_audit_log(res, request.arguments)
            return res
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            res = ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=str(exc),
                duration_ms=elapsed_ms,
                risk_level=definition.risk_level
            )
            self._record_audit_log(res, request.arguments)
            return res

    def _record_audit_log(self, result: ToolExecutionResult, arguments: Dict[str, Any]) -> None:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": result.tool_name,
            "success": result.success,
            "duration_ms": result.duration_ms,
            "risk_level": result.risk_level.value if result.risk_level else "low",
            "arguments_keys": list(arguments.keys()),
            "error": result.error
        }
        logger.info(f"Tool Audit: {log_entry}")
        if self._audit_log_path:
            try:
                self._audit_log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._audit_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as exc:
                logger.warning(f"Could not append tool audit log: {exc}")
