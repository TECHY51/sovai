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
