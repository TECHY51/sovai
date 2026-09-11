# SovAI — Living Roadmap

This document is the single source of truth for the implementation status of **SovAI**, a sovereign on-premise agentic AI workbench for confidential industrial knowledge work.

## Status Legend
* `NOT STARTED`: Scope defined; no implementation has begun.
* `IN PROGRESS`: Active development and unit validation underway.
* `BLOCKED`: Blocked by dependency, hardware, or external constraint.
* `IMPLEMENTED`: Code written, pending complete integration testing.
* `TESTED`: Automated and integration tests passing.
* `COMPLETED`: All acceptance criteria verified and documented; exit condition met.

---

## Phase Summary

| Phase | Title | Status | Primary Output |
|---|---|---|---|
| **Phase 0** | Repository & Roadmap | **COMPLETED** | Repository structure, living roadmap, backend & frontend skeletons |
| **Phase 1** | Local Model Infrastructure | **COMPLETED** | Local model provider abstraction & runtime integration |
| **Phase 2** | Model Registry | **COMPLETED** | Centralized model capability registry & configuration |
| **Phase 3** | Task Router | **COMPLETED** | Automatic task-to-model selector |
| **Phase 4** | Agent Orchestrator | **COMPLETED** | Stateful agent loop (Understand → Plan → Route → Act → Verify → Deliver) |
| **Phase 5** | Tool Registry | **COMPLETED** | Controlled, schema-validated tool execution layer |
| **Phase 6** | Secure Python Sandbox | NOT STARTED | Isolated process execution with zero network & strict resource limits |
| **Phase 7** | Local Knowledge Base / RAG | NOT STARTED | Local document ingestion, chunking, embeddings & grounded retrieval |
| **Phase 8** | Multimodal Processing | NOT STARTED | Local OCR and vision pipeline for documents, P&IDs, and images |
| **Phase 9** | Artifact Generation | NOT STARTED | Deterministic DOCX, XLSX, PPTX deliverable generators |
| **Phase 10** | Verification Engine | NOT STARTED | Automated validation of code, calculations, documents, and RAG claims |
| **Phase 11** | Human Approval Layer | NOT STARTED | Gated human-in-the-loop review for consequential agent actions |
| **Phase 12** | Security & Sovereignty | NOT STARTED | Outbound traffic monitoring, audit logging, air-gap demonstration |
| **Phase 13** | Frontend Workbench | NOT STARTED | Full-featured operator workbench UI |
| **Phase 14** | End-to-End Demo Workflows | NOT STARTED | 3 verified industrial workflows (Inspection, Coding, P&ID) |
| **Phase 15** | Testing & Evaluation | NOT STARTED | Comprehensive test suite and factual evaluation |
| **Phase 16** | Failure Handling & Reliability | NOT STARTED | Graceful degradation, sandboxed recovery, fail-closed security |
| **Phase 17** | Offline Deployment | NOT STARTED | Self-contained, zero-internet on-premise packaging |
| **Phase 18** | Final Hardening | NOT STARTED | Dead code elimination, audit verification, production readiness |

---

## Detailed Phase Tracking

### Phase 0 — Repository & Roadmap
* **Goal**: Establish the repository structure, engineering conventions, living documentation, and operational skeletons.
* **Tasks**:
  * Create repository directory hierarchy (`frontend`, `backend`, `docs`, `models`, `knowledge_base`, `sandbox`, `data`, `deployment`, `security`, `scripts`, `tests`).
  * Create `README.md`, `docs/ROADMAP.md`, `docs/PHASE_LOG.md`, `.env.example`, `.gitignore`.
  * Implement FastAPI backend skeleton with `/api/health` endpoint.
  * Implement Vite + React frontend skeleton with clean build.
  * Implement automated health check tests.
* **Dependencies**: Python 3.12+, Node.js 20+.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] Repository structure exists.
  * [x] `README.md` exists and contains setup/run instructions.
  * [x] `.env.example` exists with documented variables.
  * [x] `docs/ROADMAP.md` contains all project phases.
  * [x] `docs/PHASE_LOG.md` exists.
  * [x] The backend skeleton starts without an import/runtime error.
  * [x] The frontend skeleton starts without a build error.
  * [x] A basic health check endpoint returns success.
  * [x] No placeholder file is falsely presented as a completed subsystem.
* **Implemented**: Directory structure, `.gitignore`, `.env.example`, `docs/ROADMAP.md`, `docs/PHASE_LOG.md`, `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/api/health.py`, `frontend/`, `tests/unit/test_health.py`.
* **Tested**: Pytest 3/3 passed; Vite build succeeded; Uvicorn live server HTTP 200 confirmed.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 1 — Local Model Infrastructure.

---

### Phase 1 — Local Model Infrastructure
* **Goal**: Run local models (`Qwen2.5-Coder-3B`, `Qwen3-4B`, `Gemma 3 4B`) through a unified provider abstraction without external APIs.
* **Tasks**:
  * Create `ModelProvider` interface (`generate`, `stream`, `health`, `capabilities`).
  * Implement `OllamaProvider` connected to local Ollama runtime on port 11434.
  * Pull and verify local models on RTX 4050 6GB GPU: `qwen2.5-coder:3b`, `qwen3:4b`, `gemma3:4b`.
  * Support thinking/reasoning token streams from `qwen3:4b`.
  * Implement `/api/models/health` and `/api/models/capabilities/{model}`.
  * Implement automated integration tests for reachability, inference, and controlled error handling.
* **Dependencies**: Phase 0.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] Qwen2.5-Coder-3B is reachable locally.
  * [x] Qwen3-4B is reachable locally.
  * [x] Gemma 3 4B is reachable locally for verified capabilities only.
  * [x] Each model successfully handles at least one verified test request.
  * [x] Backend can invoke each model through the common provider abstraction.
  * [x] Provider health checks report accurate status.
  * [x] An unavailable model produces a controlled error.
  * [x] No cloud API is required for these tests.
  * [x] Actual model/runtime versions and endpoints are documented.
* **Implemented**: `backend/app/models/base.py`, `backend/app/models/ollama.py`, `backend/app/models/__init__.py`, `backend/app/api/models.py`, `tests/integration/test_models.py`.
* **Tested**: 8/8 model integration tests passed, full suite 11/11 passed in 24.9s.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 2 — Model Registry.

---

### Phase 2 — Model Registry
* **Goal**: Centralized configuration-driven registry for available models and verified capabilities.
* **Tasks**:
  * Build model registry loading configuration from file/environment.
  * Register Qwen2.5-Coder-3B, Qwen3-4B, Gemma 3 4B.
  * Implement discovery and availability checks.
* **Dependencies**: Phase 1.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] All three current models are registered.
  * [x] Registry entries contain verified capabilities only.
  * [x] Registry can list available models.
  * [x] Registry can identify unavailable models.
  * [x] Model metadata is loaded from configuration rather than scattered hard-coded logic.
  * [x] A model can be added without modifying unrelated agent/tool code.
  * [x] Registry tests cover valid and invalid configurations.
* **Implemented**: `backend/app/models/registry.py`, `models/registry.yaml`, `backend/app/api/models.py` (`/api/models/registry`), `tests/unit/test_registry.py`, `tests/integration/test_registry_sync.py`.
* **Tested**: 5/5 unit tests passed, 5/5 integration tests passed with live provider synchronization.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 3 — Task Router.

---

### Phase 3 — Task Router
* **Goal**: Automatically select the optimal model based on task classification.
* **Tasks**:
  * Build deterministic capability matcher for coding, reasoning, and vision tasks.
  * Produce structured routing outputs specifying model and permitted tools.
  * Integrate with `ModelRegistry` ensuring no unavailable models are selected.
  * Implement fallback and clarification paths for ambiguous queries.
  * Audit log routing decisions.
* **Dependencies**: Phase 2.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] Coding request routes to Qwen2.5-Coder-3B.
  * [x] Reasoning/general request routes to Qwen3-4B.
  * [x] Vision request routes to Gemma 3 4B only when capability is verified.
  * [x] Router returns structured output.
  * [x] Router never selects an unavailable model.
  * [x] Ambiguous requests produce documented fallback or clarification.
  * [x] At least two task classes are routed to different models.
  * [x] Routing decisions are logged.
* **Implemented**: `backend/app/router/router_schema.py`, `backend/app/router/task_router.py`, `backend/app/router/__init__.py`, `backend/app/api/router.py`, `tests/unit/test_router.py`, `tests/integration/test_router_api.py`.
* **Tested**: 8/8 unit tests passed, 6/6 integration tests passed, full suite 35/35 tests passed.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 4 — Agent Orchestrator.

---

### Phase 4 — Agent Orchestrator
* **Goal**: Implement the stateful agent execution loop: Understand → Plan → Route → Act → Observe → Verify → Iterate → Deliver.
* **Tasks**:
  * Implement explicit agent state machine and execution trace recording.
  * Support multi-step planning, tool invocation, result observation, and retries.
  * Integrate with Tool Registry and Task Router for coordinated model-tool workflows.
* **Dependencies**: Phase 3.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] Agent maintains explicit task state.
  * [x] Agent can create and execute a multi-step plan.
  * [x] Agent can invoke at least two different tools in a single workflow.
  * [x] Tool results are returned to the agent.
  * [x] Agent can decide whether another step is required.
  * [x] At least one failed step produces a controlled retry or failure path.
  * [x] Agent execution trace records major steps.
  * [x] Agent successfully completes one end-to-end multi-step test task.
* **Implemented**: `backend/app/agent/agent_schema.py`, `backend/app/agent/agent_orchestrator.py`, `backend/app/agent/__init__.py`, `backend/app/api/agent.py`, `backend/app/tools/tool_schema.py`, `backend/app/tools/tool_registry.py`, `tests/unit/test_agent.py`, `tests/integration/test_agent_api.py`.
* **Tested**: 7/7 unit tests passed, 5/5 integration tests passed, full suite 47/47 tests passed.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 5 — Tool Registry.

---

### Phase 5 — Tool Registry
* **Goal**: Create a schema-validated, permission-controlled tool execution layer.
* **Tasks**:
  * Build central tool registry with machine-readable schemas and risk levels.
  * Implement complete initial tool suite: `read_file`, `write_file`, `list_files`, `search_documents`, `calculate`, `run_python`, `ocr_document`, `analyze_image`, `create_docx`, `create_xlsx`, `create_pptx`.
  * Enforce strict workspace path boundary confinement and reject path traversal attacks.
  * Check permission context before execution and fail closed on unauthorized requests.
  * Record all tool executions in audit log (`data/logs/tool_executions.jsonl`).
* **Dependencies**: Phase 4.
* **Status**: COMPLETED
* **Acceptance Criteria**:
  * [x] Every enabled tool is registered centrally.
  * [x] Every tool has a machine-readable schema.
  * [x] Invalid arguments are rejected before execution.
  * [x] Tool permissions are checked before execution.
  * [x] Tool executions are logged.
  * [x] Agent can discover only allowlisted tools.
  * [x] Unknown tools cannot be executed by model-generated requests.
  * [x] Filesystem tools enforce configured path boundaries.
  * [x] Tool registry has automated tests.
* **Implemented**: `backend/app/tools/tool_schema.py`, `backend/app/tools/tool_registry.py`, `backend/app/tools/__init__.py`, `backend/app/api/tools.py`, `tests/unit/test_tools.py`, `tests/integration/test_tools_api.py`.
* **Tested**: 9/9 unit tests passed, 7/7 integration tests passed, full suite 63/63 tests passed.
* **Known Issues**: None.
* **Pending**: None.
* **Next Step**: Phase 6 — Secure Python Sandbox.

---

### Phase 6 — Secure Python Sandbox
* **Goal**: Safely execute generated code in an isolated environment with zero network access and strict resource boundaries.
* **Tasks**:
  * Create sandbox runner enforcing timeouts, memory limits, and isolated temporary workspaces.
  * Test network blocking and filesystem confinement.
* **Dependencies**: Phase 5.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Valid Python code executes successfully.
  * [ ] Syntax errors are captured without backend crash.
  * [ ] Infinite loops are terminated by timeout.
  * [ ] Memory/CPU limits are enforced.
  * [ ] Network access from sandbox is blocked and tested.
  * [ ] Sandbox cannot access files outside workspace in tested cases.
  * [ ] Temporary execution data is isolated from persistent application data.
  * [ ] Sandbox process terminates cleanly after execution.
  * [ ] Execution stdout/stderr/status are captured.
  * [ ] Security tests pass.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 5.
* **Next Step**: Implement after Phase 5.

---

### Phase 7 — Local Knowledge Base / RAG
* **Goal**: Provide local organizational knowledge retrieval with grounded citations and zero external network calls.
* **Tasks**:
  * Ingest PDF, DOCX, TXT documents into local chunks.
  * Generate local embeddings and execute vector search with source metadata.
* **Dependencies**: Phase 1, Phase 5.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] PDF, DOCX, TXT ingestion works locally.
  * [ ] Documents are chunked and indexed locally.
  * [ ] Embeddings generated locally.
  * [ ] Retrieval returns source metadata (document, page, section).
  * [ ] Retrieved content feeds reasoning workflow.
  * [ ] Known test question retrieves expected source.
  * [ ] Unsupported question does not fabricate a source.
  * [ ] Operates without external services at runtime.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 6.
* **Next Step**: Implement after Phase 6.

---

### Phase 8 — Multimodal Processing
* **Goal**: Local OCR and vision pipeline for scanned documents, engineering drawings, and images.
* **Tasks**:
  * Build file type detector, local OCR engine, and Gemma 3 4B vision interface.
  * Process scanned PDFs and visual engineering artifacts.
* **Dependencies**: Phase 1, Phase 5.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Identifies supported document/image types.
  * [ ] At least one scanned PDF processed locally.
  * [ ] OCR output is captured and inspectable.
  * [ ] At least one image processed locally with verified model capabilities.
  * [ ] Known test image produces expected class of information.
  * [ ] Failures return controlled errors.
  * [ ] Zero external OCR or vision APIs required.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 7.
* **Next Step**: Implement after Phase 7.

---

### Phase 9 — Artifact Generation
* **Goal**: Deterministic generation of enterprise DOCX, XLSX, and PPTX business deliverables from structured model output.
* **Tasks**:
  * Implement document generators using python-docx, openpyxl, python-pptx.
  * Validate structural file integrity and register with Artifact Manager.
* **Dependencies**: Phase 5.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Valid DOCX, XLSX, and PPTX can be generated and opened cleanly.
  * [ ] Generated files contain expected test content.
  * [ ] Output paths controlled by backend.
  * [ ] Generated artifacts registered in Artifact Manager.
  * [ ] Failures handled cleanly without crashing.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 8.
* **Next Step**: Implement after Phase 8.

---

### Phase 10 — Verification Engine
* **Goal**: Verify generated code, calculations, documents, and RAG grounding before delivery.
* **Tasks**:
  * Build verification modules for code execution results, numerical sanity checks, document structure, and RAG citation grounding.
* **Dependencies**: Phase 6, Phase 7, Phase 9.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Code verification runs code in sandbox before marking verified.
  * [ ] Calculation verification compares generated values with independent math.
  * [ ] Document verification confirms structural validity.
  * [ ] RAG verification checks supporting retrieved evidence.
  * [ ] Failed verification returns non-success status and triggers agent retry.
  * [ ] Verification results are logged.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 9.
* **Next Step**: Implement after Phase 9.

---

### Phase 11 — Human Approval Layer
* **Goal**: Gated human review for consequential actions (document release, code execution).
* **Tasks**:
  * Implement approval checkpoint state in agent workflow.
  * Support approve, reject, and revise actions with complete audit logging.
* **Dependencies**: Phase 4, Phase 10.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Agent pauses before configured consequential action.
  * [ ] User can approve, reject, or edit proposed output.
  * [ ] Rejected actions do not proceed.
  * [ ] Approvals/rejections are logged in audit trail.
  * [ ] Agent state remains recoverable.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 10.
* **Next Step**: Implement after Phase 10.

---

### Phase 12 — Security & Sovereignty
* **Goal**: Demonstrable sovereignty: network monitoring, audit logs, outbound traffic blocking.
* **Tasks**:
  * Implement network traffic observer and outbound socket policy.
  * Build security status API reporting real connection and audit metrics.
* **Dependencies**: Phase 0, Phase 6.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Outbound network policy configured and tested.
  * [ ] External traffic blocked per deployment policy.
  * [ ] Network monitoring records connection attempts.
  * [ ] Security dashboard reads actual monitoring data (no fabricated values).
  * [ ] Controlled external connection test verifies block.
  * [ ] Audit logs capture tool executions with timestamps.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 11.
* **Next Step**: Implement after Phase 11.

---

### Phase 13 — Frontend Workbench
* **Goal**: Modern web interface providing Chat, Tasks, Knowledge, Models, Artifacts, and Security views.
* **Tasks**:
  * Build full workbench views, execution trace visualizations, file uploader, and artifact previews.
* **Dependencies**: Phase 0, Phase 4, Phase 12.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] User can execute tasks and view execution trace in browser.
  * [ ] File upload works for supported types.
  * [ ] Model selection and tool execution visible in real-time.
  * [ ] Generated artifacts accessible and downloadable.
  * [ ] Security and network status displayed accurately.
  * [ ] Frontend never calls model server directly.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 12.
* **Next Step**: Implement after Phase 12.

---

### Phase 14 — End-to-End Demo Workflows
* **Goal**: Stabilize and verify the three primary industrial workflows:
  1. Inspection Report → Approval DOCX
  2. Coding Request → Sandboxed Verified Code
  3. P&ID / Image → Vision Analysis
* **Dependencies**: Phases 1 through 13.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Demo 1: Inspection PDF → OCR → SOP retrieval → Reasoning → DOCX → Verification passes.
  * [ ] Demo 2: Coding request → Qwen2.5-Coder → Sandbox execution → Verification passes.
  * [ ] Demo 3: Image/P&ID → Gemma 3 4B → Interpretable visual analysis passes.
  * [ ] All three workflows pass consecutively with visible security evidence.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 13.
* **Next Step**: Implement after Phase 13.

---

### Phase 15 — Testing & Evaluation
* **Goal**: Comprehensive automated testing suite (unit, integration, security, e2e) and factual evaluations.
* **Dependencies**: Phase 14.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Unit, integration, security, and e2e test suites pass.
  * [ ] Router, agent, RAG, vision, sandbox, and artifact evaluations recorded factually.
  * [ ] Zero benchmark fabrication.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 14.
* **Next Step**: Implement after Phase 14.

---

### Phase 16 — Failure Handling & Reliability
* **Goal**: Graceful degradation, controlled error reporting, and fail-closed security for all failure modes.
* **Dependencies**: Phase 15.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Model unavailable, tool failure, OCR failure, RAG failure, sandbox timeout handled cleanly.
  * [ ] Application remains running; no uncontrolled crashes.
  * [ ] Security failures fail closed.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 15.
* **Next Step**: Implement after Phase 15.

---

### Phase 17 — Offline Deployment
* **Goal**: Self-contained, zero-internet on-premise installation package and procedures.
* **Dependencies**: Phase 16.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] Offline installation procedure verified in fresh environment.
  * [ ] Zero external dependencies fetched at runtime.
  * [ ] Health checks confirm service health.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 16.
* **Next Step**: Implement after Phase 16.

---

### Phase 18 — Final Hardening
* **Goal**: System audit, dead code elimination, documentation synchronization, and final production validation.
* **Dependencies**: Phase 17.
* **Status**: NOT STARTED
* **Acceptance Criteria**:
  * [ ] All mandatory MVP capabilities tested.
  * [ ] All three end-to-end demos pass consecutively.
  * [ ] Critical security tests pass.
  * [ ] ROADMAP, PHASE_LOG, and README reflect actual tested state.
  * [ ] Exit condition met for final completion.
* **Implemented**: None.
* **Tested**: None.
* **Known Issues**: None.
* **Pending**: Awaiting Phase 17.
* **Next Step**: Final audit.
