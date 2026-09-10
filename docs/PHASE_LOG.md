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
