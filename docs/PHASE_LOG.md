# SovAI — Phase Changelog

This document maintains an immutable audit log of architectural decisions, file changes, test executions, and acceptance criteria verification at the conclusion of every phase.

---

## Phase 0: Repository & Roadmap

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Establish the repository hierarchy, living documentation (`ROADMAP.md`, `PHASE_LOG.md`), operational configurations (`.env.example`, `.gitignore`), FastAPI backend skeleton with `/api/health`, and Vite + React frontend skeleton.

### Architectural Decisions
1. **Separation of Concerns**: Kept backend and frontend decoupled. Frontend communicates strictly via `/api` proxying to FastAPI backend; frontend has no direct access to model servers or privileged tools.
2. **Deterministic Health Check**: The `/api/health` endpoint returns explicit subsystem readiness (`READY` vs `PENDING` vs `BLOCKED`), avoiding any hallucinated claims of completion.
3. **Multi-Environment Support**: Supported both native Windows execution (Python 3.12, Node.js 24, npm 11) and containerized / WSL2 Ubuntu environments.

### Files Added / Modified
* `.gitignore`: Core exclusion rules for Python caches, virtual environments, node modules, temporary sandbox executions, and model weights.
* `.env.example`: Documented environment variables for server ports, model endpoints (`Qwen2.5-Coder-3B`, `Qwen3-4B`, `Gemma 3 4B`), sandbox limits, and sovereignty enforcement.
* `docs/ROADMAP.md`: Complete living roadmap covering Phase 0 through Phase 18 with explicit acceptance criteria.
* `docs/PHASE_LOG.md`: Phase changelog document.
* `docs/architecture/overview.md`: System architecture overview.
* `backend/requirements.txt`: Python package specifications.
* `backend/app/main.py`: Main FastAPI application factory.
* `backend/app/core/config.py`: Application settings using Pydantic Settings.
* `backend/app/api/health.py`: Health check router with factual subsystem status tracking.
* `frontend/package.json`: Vite + React frontend configuration.
* `frontend/vite.config.js`: Vite dev server configuration with `/api` reverse proxy.
* `frontend/index.html`: Responsive HTML entry with typography.
* `frontend/src/index.css`: Vanilla CSS design system matching dark workbench specs.
* `frontend/src/App.jsx`: Responsive workbench overview UI.
* `tests/conftest.py`: Pytest configuration.
* `tests/unit/test_health.py`: Automated tests for `/` and `/api/health`.
* `README.md`: Project documentation and run commands.

### Acceptance Criteria Evaluation
* [x] Repository structure exists: PASS.
* [x] `README.md` exists and contains setup/run instructions: PASS.
* [x] `.env.example` exists with documented variables: PASS.
* [x] `docs/ROADMAP.md` contains all project phases: PASS.
* [x] `docs/PHASE_LOG.md` exists: PASS.
* [x] The backend skeleton starts without an import/runtime error: PASS (verified via pytest and live uvicorn process).
* [x] The frontend skeleton starts without a build error: PASS (verified via `vite build`, built in 700ms).
* [x] A basic health check endpoint returns success: PASS (HTTP 200 with complete JSON schema).
* [x] No placeholder file is falsely presented as a completed subsystem: PASS (subsystems explicitly marked PENDING in health payload and READMEs).

### Tests Executed
* `python -m pytest tests/unit/test_health.py -v`: 3 passed in 1.50s.
* `npm run build` (frontend): Built cleanly with 0 errors.
* `curl.exe -s http://127.0.0.1:8000/api/health`: Returned status 200 with valid health telemetry payload.

### Next Phase
* Phase 1: Local Model Infrastructure.

---

## Phase 1: Local Model Infrastructure

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Establish a decoupled, provider-agnostic inference layer (`ModelProvider` base abstraction) and connect SovAI to the verified local inference runtime hosting the three required models on the NVIDIA RTX 4050 6GB GPU environment:
1. `Qwen2.5-Coder-3B` (`qwen2.5-coder:3b`)
2. `Qwen3-4B` (`qwen3:4b`)
3. `Gemma 3 4B` (`gemma3:4b`)

### Architectural Decisions
1. **Extensible Provider Abstraction**: Created `ModelProvider` ABC (`generate`, `stream`, `health`, `capabilities`) to decouple SovAI from any single inference engine.
2. **Ollama Integration**: Built `OllamaProvider` connecting via `httpx.AsyncClient` to local Ollama runtime on `http://127.0.0.1:11434`.
3. **Reasoning Tokens Capture**: Discovered and implemented support for `qwen3:4b`'s separate `thinking` stream, preserving internal reasoning traces while preventing empty response fallbacks.
4. **Verified Capability Gating**: Multimodal capability is confirmed explicitly for `gemma3:4b` and gated from text-only models.
5. **Controlled Error Boundaries**: Nonexistent models and network disconnects raise structured `ModelError` with HTTP 404/503 status rather than unhandled 500 exceptions.

### Files Added / Modified
* `backend/app/models/base.py`: Abstract `ModelProvider`, `ModelResponse`, `ProviderHealth`, `ModelCapabilities`, `ModelError`.
* `backend/app/models/ollama.py`: Concrete `OllamaProvider` implementation with streaming, thinking token parsing, and capability detection.
* `backend/app/models/__init__.py`: Factory function `get_model_provider()` and exports.
* `backend/app/api/models.py`: API routes `/api/models/health`, `/api/models/capabilities/{model}`, `/api/models/test`.
* `backend/app/api/health.py`: Dynamically checks model provider reachability to report `model_infrastructure` readiness.
* `backend/app/main.py`: Included `models_router`.
* `tests/integration/test_models.py`: Automated integration tests covering provider health, generation across all 3 models, capabilities, and 404 controlled errors.
* `tests/unit/test_health.py`: Updated assertions reflecting `model_infrastructure` readiness.

### Acceptance Criteria Evaluation
* [x] Qwen2.5-Coder-3B is reachable locally: PASS (`qwen2.5-coder:3b` generated valid Python function).
* [x] Qwen3-4B is reachable locally: PASS (`qwen3:4b` generated valid reasoning content and thinking tokens).
* [x] Gemma 3 4B is reachable locally for only verified capabilities: PASS (`gemma3:4b` verified with `supports_vision=True`).
* [x] Each model successfully handles at least one verified test request: PASS (all 3 models passed generation tests).
* [x] Backend can invoke each model through common provider abstraction: PASS (`ModelProvider.generate`).
* [x] Provider health checks report accurate status: PASS (`/api/models/health` reports reachable and lists all 3 models).
* [x] An unavailable model produces a controlled error: PASS (`ModelError` status code 404, HTTP 404 returned without crashing).
* [x] No cloud API is required for these tests: PASS (100% on-premise execution on local RTX 4050 GPU).
* [x] Actual model/runtime versions and endpoints documented: PASS (Ollama 0.34.0, RTX 4050 Laptop GPU 6GB, `http://127.0.0.1:11434`).

### Tests Executed
* `python -m pytest tests/integration/test_models.py -v`: 8/8 passed in 23.28s.
* `python -m pytest tests -v`: 11/11 passed in 24.93s.

### Next Phase
* Phase 2: Model Registry.

---

## Phase 2: Model Registry

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Establish a centralized, configuration-driven registry for available models and verified capabilities. Decouple model discovery and metadata from routing and tool logic. Support dynamic availability checks via live provider inspection.

### Architectural Decisions
1. **Configuration-Driven Manifests**: Model configurations loaded from `models/registry.yaml` rather than hardcoded in business logic.
2. **Strict Verification Gating**: Only models and capabilities verified in Phase 1 (`qwen2.5-coder:3b`, `qwen3:4b`, `gemma3:4b`) are declared with active capabilities.
3. **Dynamic Availability Synchronization**: The `sync_availability()` method queries the active `ModelProvider` to mark models `AVAILABLE` or `UNAVAILABLE` without restarting the server.
4. **Offline Detection Verification**: Included `offline-test-model` (`nonexistent-model:99b`) to guarantee that unavailable models are accurately recognized and gated.
5. **Decoupled Architecture**: Models can be added or updated via YAML or runtime registration without touching agent, router, or tool code.

### Files Added / Modified
* `backend/app/models/registry.py`: `ModelRegistry`, `ModelMetadata`, `ModelCapabilitiesInfo`, `ModelCategory`, `ModelStatus`.
* `models/registry.yaml`: YAML configuration for coding, reasoning, vision, and offline test models.
* `backend/app/models/__init__.py`: Singleton factory `get_model_registry()`.
* `backend/app/api/models.py`: API routes `/api/models/registry`, `/api/models/registry/{model_id}`, `/api/models/registry/sync`.
* `backend/app/api/health.py`: Dynamically checks model registry readiness.
* `tests/unit/test_registry.py`: 5 unit tests for YAML loading, filtering, dynamic addition, and invalid config rejection.
* `tests/integration/test_registry_sync.py`: 5 integration tests for live provider synchronization and API endpoints.

### Acceptance Criteria Evaluation
* [x] All three current models are registered: PASS (`qwen2.5-coder-3b`, `qwen3-4b`, `gemma3-4b` in `models/registry.yaml`).
* [x] Registry entries contain verified capabilities only: PASS (no unverified modalities or capabilities added).
* [x] Registry can list available models: PASS (`registry.list_models(available_only=True)` and `GET /api/models/registry?available_only=true`).
* [x] Registry can identify unavailable models: PASS (`offline-test-model` confirmed `UNAVAILABLE`).
* [x] Model metadata is loaded from configuration rather than scattered hard-coded logic: PASS (`models/registry.yaml`).
* [x] A model can be added without modifying unrelated agent/tool code: PASS (verified in `test_registry_dynamic_model_addition`).
* [x] Registry tests cover valid and invalid configurations: PASS (missing file, malformed yaml, missing fields all tested).

### Tests Executed
* `python -m pytest tests/unit/test_registry.py -v`: 5/5 passed in 0.17s.
* `python -m pytest tests/integration/test_registry_sync.py -v`: 5/5 passed in 2.12s.
* Full test suite `pytest tests -v`: 21/21 passed in 29.84s.

### Next Phase
* Phase 3: Task Router.

---

## Phase 3: Task Router

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Build an automatic task-to-model selector that routes coding requests to `Qwen2.5-Coder-3B`, reasoning/general requests to `Qwen3-4B`, and visual/multimodal requests to `Gemma 3 4B`. Integrate routing with `ModelRegistry` so that unavailable models are never selected, generate structured schemas with tool permissions, provide fallback and clarification paths for ambiguous queries, and log all routing decisions for auditing.

### Architectural Decisions
1. **Deterministic Heuristics & Capability Matcher**: Precompiled regex patterns and file extension detectors classify prompts reliably without incurring extra LLM latency before task execution.
2. **Registry-Gated Model Selection**: The router queries `ModelRegistry` and actively checks `model.status == ModelStatus.AVAILABLE`. If a preferred model is offline, the router falls back gracefully to an available model or triggers a clarification/warning flag rather than failing silently or selecting an unreachable endpoint.
3. **Structured Output Contracts**: `RoutingDecision` schema includes `task_type`, `model_id`, `model_tag`, permitted `tools`, `confidence`, `reasoning`, `fallback_used`, and `clarification_needed`.
4. **Audit-Ready Logging**: Decisions are recorded in memory (`_history`), emitted to application logs, and appended to `data/logs/routing_audit.jsonl` with timestamps and request context.
5. **REST API & Telemetry**: Exposed `/api/router/route`, `/api/router/history`, `/api/router/mappings`, and updated `/api/health` reporting `task_router` as `READY` (Phase 3).

### Files Added / Modified
* `backend/app/router/router_schema.py`: `TaskType`, `RoutingRequest`, `RoutingDecision` Pydantic models.
* `backend/app/router/task_router.py`: `TaskRouter` implementation with deterministic classification, registry validation, and audit recording.
* `backend/app/router/__init__.py`: Singleton factory `get_task_router()` and public exports.
* `backend/app/api/router.py`: FastAPI routes for `/api/router/route`, `/api/router/history`, and `/api/router/mappings`.
* `backend/app/main.py`: Included `router_router` in application factory.
* `backend/app/api/health.py`: Updated `task_router` subsystem status to `READY`.
* `models/registry.yaml`: Explicit baseline statuses configured (`available` for verified models, `unavailable` for offline test model).
* `tests/unit/test_router.py`: 8 unit tests covering coding, reasoning, vision, file attachments, ambiguous queries, unavailable model avoidance, and history logging.
* `tests/integration/test_router_api.py`: 6 integration tests verifying `/api/router/route` endpoints, mappings, and health reporting.
* `tests/unit/test_health.py`: Updated assertions reflecting `task_router` readiness and `agent_orchestrator` pending status.

### Acceptance Criteria Evaluation
* [x] Coding test request routes to Qwen2.5-Coder-3B: PASS (`test_coding_request_routes_to_qwen25_coder` and `/api/router/route` verified).
* [x] Reasoning/general test request routes to Qwen3-4B: PASS (`test_reasoning_request_routes_to_qwen3` and `/api/router/route` verified).
* [x] Vision request routes to Gemma 3 4B only when capability is verified: PASS (`test_vision_request_routes_to_gemma3_multimodal` and `/api/router/route` verified).
* [x] Router returns structured output: PASS (`RoutingDecision` schema verified).
* [x] Router never selects an unavailable model: PASS (`test_router_never_selects_unavailable_model` verified).
* [x] Ambiguous requests produce a documented fallback or clarification path: PASS (`clarification_needed=True` with prompt returned).
* [x] At least two task classes are routed to different models: PASS (`qwen2.5-coder-3b` vs `qwen3-4b` verified).
* [x] Routing decisions are logged: PASS (`_record_decision` verified in memory and audit log).

### Tests Executed
* `python -m pytest tests/unit/test_router.py -v`: 8/8 passed in 0.18s.
* `python -m pytest tests/integration/test_router_api.py -v`: 6/6 passed in 0.83s.
* Full test suite `pytest tests -v`: 35/35 passed in 30.78s.
* Frontend build `cmd.exe /c "npm run build"`: Built cleanly in 628ms.

### Next Phase
* Phase 4: Agent Orchestrator.

---

## Phase 4: Agent Orchestrator

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Transform SovAI from a single-turn query engine into an autonomous, stateful agentic system implementing the full industrial lifecycle:
$$\text{Understand} \longrightarrow \text{Plan} \longrightarrow \text{Route} \longrightarrow \text{Act} \longrightarrow \text{Observe} \longrightarrow \text{Verify} \longrightarrow \text{Iterate} \longrightarrow \text{Deliver}$$
Maintain explicit task state, construct multi-step execution plans, invoke multiple tools within a single task, capture execution traces, handle controlled failure retries, and deliver verified final deliverables.

### Architectural Decisions
1. **Explicit State Machine**: Implemented `AgentState` with discrete lifecycle stages (`CREATED`, `PLANNING`, `ROUTING`, `EXECUTING`, `VERIFYING`, `ITERATING`, `COMPLETED`, `FAILED`), preserving the full plan, variables, retry counter, and timestamped trace events.
2. **Foundational Tool Registry**: Built initial safe tools layer (`calculate` with safe AST parsing, `write_file`, `read_file`, `list_files` with strict workspace confinement) to enable deterministic multi-tool agent execution without circular dependencies.
3. **Execution Trace Logging**: Every step transition records a `TraceEvent` with stage, step number, action, parameters, duration in milliseconds, and status.
4. **Controlled Failure & Repair Loop**: When a tool execution fails, the orchestrator transitions to `ITERATING`, increments `retry_count`, attempts parameter repair (e.g. division-by-zero or missing file mitigation), and records the iteration in the audit trail.
5. **REST API & Telemetry**: Exposed `/api/agent/run`, `/api/agent/tasks`, `/api/agent/tasks/{task_id}`, and `/api/agent/tasks/{task_id}/trace`. Updated `/api/health` reporting `agent_orchestrator` as `READY` (Phase 4).

### Files Added / Modified
* `backend/app/tools/tool_schema.py`: Tool definition, parameters, execution request, and result contracts.
* `backend/app/tools/tool_registry.py`: Safe AST calculator, workspace path confinement, and tool execution registry.
* `backend/app/tools/__init__.py`: Singleton factory `get_tool_registry()`.
* `backend/app/agent/agent_schema.py`: `TaskStatus`, `PlanStep`, `TraceEvent`, `AgentState`, and `AgentRunRequest`.
* `backend/app/agent/agent_orchestrator.py`: `AgentOrchestrator` core engine with multi-step planning, tool invocation, retry handling, and execution tracing.
* `backend/app/agent/__init__.py`: Singleton factory `get_agent_orchestrator()`.
* `backend/app/api/agent.py`: FastAPI routes for agent execution, task inspection, and execution traces.
* `backend/app/main.py`: Included `agent_router` in application factory.
* `backend/app/api/health.py`: Updated `agent_orchestrator` subsystem status to `READY`.
* `tests/unit/test_agent.py`: 7 unit tests covering state management, planning, multiple tools, retries, traces, and task persistence.
* `tests/integration/test_agent_api.py`: 5 integration tests verifying live multi-step execution, task inspection, and health reporting.
* `tests/unit/test_health.py`: Updated assertions reflecting `agent_orchestrator` readiness and `tool_registry` pending status.

### Acceptance Criteria Evaluation
* [x] Agent maintains explicit task state: PASS (`AgentState` validated with full plan, variables, retry counts, trace).
* [x] Agent can create and execute a multi-step plan: PASS (`test_agent_creates_and_executes_multistep_plan` verified).
* [x] Agent can invoke at least two different tools in a single workflow: PASS (`calculate` + `write_file`/`read_file` verified in single run).
* [x] Tool results are returned to the agent: PASS (`step.result` and `state.variables` capture tool outputs).
* [x] Agent can decide whether another step is required: PASS (iterative step progression verified).
* [x] At least one failed step produces a controlled retry or failure path: PASS (`test_agent_controlled_retry_on_failure` verified).
* [x] Agent execution trace records major steps: PASS (`understand`, `route`, `plan`, `act`, `observe`, `verify`, `deliver` verified in trace).
* [x] Agent successfully completes one end-to-end multi-step test task: PASS (`test_api_run_agent_multistep_workflow` verified).

### Tests Executed
* `python -m pytest tests/unit/test_agent.py -v`: 7/7 passed in 0.19s.
* `python -m pytest tests/integration/test_agent_api.py -v`: 5/5 passed in 0.84s.
* Full test suite `pytest tests -v`: 47/47 passed in 27.29s.
* Frontend build `cmd.exe /c "npm run build"`: Built cleanly in 617ms.

### Next Phase
* Phase 5: Tool Registry (Formalizing full tool catalog & fine-grained permission controls).

---

## Phase 5: Tool Registry

* **Date Started**: 2026-09-11
* **Date Completed**: 2026-09-11
* **Status**: COMPLETED

### Objectives
Establish a controlled, schema-validated, permission-governed tool execution layer. Register all initial tools (`read_file`, `write_file`, `list_files`, `search_documents`, `run_python`, `calculate`, `ocr_document`, `analyze_image`, `create_docx`, `create_xlsx`, `create_pptx`) with machine-readable schemas, strict argument type validation, allowlist gating, risk level controls, workspace path confinement, and execution audit logging.

### Architectural Decisions
1. **Machine-Readable Schemas**: Generated standard function calling JSON schemas (`to_json_schema()`) declaring parameter types, descriptions, and required constraints.
2. **Strict Fail-Closed Permission Gate**: Introduced `PermissionContext` (`granted_permissions`, `max_risk_level`, `allowlist`). Missing permissions, risk violations, or unknown tools are blocked before execution without leaking system exceptions.
3. **Workspace Path Confinement**: Path resolution in filesystem tools strictly checks `target.relative_to(workspace_root)`. Traversal attacks (`../`, escape sequences) raise controlled `PermissionError`.
4. **Safe Evaluation Guardrails**: Mathematical calculations use AST parsing without `eval()`, preventing arbitrary code execution.
5. **Execution Audit Log**: Every tool invocation is recorded to `data/logs/tool_executions.jsonl` with timestamps, execution duration, parameters, and risk level.
6. **REST API & Telemetry**: Exposed `/api/tools`, `/api/tools/schemas`, `/api/tools/permissions`, `/api/tools/{name}`, and `/api/tools/execute`. Updated `/api/health` reporting `tool_registry` as `READY` (Phase 5).

### Files Added / Modified
* `backend/app/tools/tool_schema.py`: Enhanced with `PermissionLevel`, `ToolRiskLevel`, `PermissionContext`, and JSON Schema generation.
* `backend/app/tools/tool_registry.py`: Central registry containing all 11 initial tools, path boundary checking, argument validation, and audit logging.
* `backend/app/tools/__init__.py`: Singleton factory `get_tool_registry()` and exports.
* `backend/app/api/tools.py`: FastAPI routes for tool catalog, JSON schema inspection, and permission-controlled execution.
* `backend/app/main.py`: Included `tools_router` in application factory.
* `backend/app/api/health.py`: Updated `tool_registry` subsystem status to `READY`.
* `tests/unit/test_tools.py`: 9 unit tests covering registration, schema export, argument validation, permission checks, risk policy, allowlisting, unknown tool blocking, path confinement, and audit logging.
* `tests/integration/test_tools_api.py`: 7 integration tests verifying `/api/tools`, schemas, permissions, single tool retrieval, execution, permission denial, and health reporting.
* `tests/unit/test_health.py`: Updated assertions reflecting `tool_registry` readiness and `sandbox` pending status.

### Acceptance Criteria Evaluation
* [x] Every enabled tool is registered centrally: PASS (11 tools registered and enabled).
* [x] Every tool has a machine-readable schema: PASS (`to_json_schema()` verified).
* [x] Invalid arguments are rejected before execution: PASS (`test_invalid_arguments_are_rejected_before_execution` verified).
* [x] Tool permissions are checked before execution: PASS (`test_tool_permissions_checked_before_execution` verified).
* [x] Tool executions are logged: PASS (`data/logs/tool_executions.jsonl` verified).
* [x] Agent can discover only allowlisted tools: PASS (`get_allowlisted_tools` verified).
* [x] Unknown tools cannot be executed by model-generated requests: PASS (`test_unknown_tools_cannot_be_executed` verified).
* [x] Filesystem tools enforce configured path boundaries: PASS (`test_filesystem_tools_enforce_path_boundaries` verified).
* [x] Tool registry has automated tests: PASS (9 unit + 7 integration tests).

### Tests Executed
* `python -m pytest tests/unit/test_tools.py -v`: 9/9 passed in 0.12s.
* `python -m pytest tests/integration/test_tools_api.py -v`: 7/7 passed in 0.83s.
* Full test suite `pytest tests -v`: 63/63 passed in 27.69s.
* Frontend build `cmd.exe /c "npm run build"`: Built cleanly in 619ms.

### Next Phase
* Phase 6: Secure Python Sandbox.




