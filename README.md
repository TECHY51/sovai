# SovAI — Sovereign Agentic AI Workbench

SovAI is an on-premise, agentic AI workbench engineered for confidential industrial knowledge work. It enables air-gapped reasoning, autonomous tool execution, document understanding, and deliverable generation without transmitting proprietary data to external cloud APIs.

## Core Execution Philosophy

$$\text{Understand} \to \text{Plan} \to \text{Route} \to \text{Act} \to \text{Observe} \to \text{Verify} \to \text{Iterate} \to \text{Deliver}$$

SovAI is **not merely a chatbot**. It is an autonomous workbench that decomposes industrial tasks, routes sub-tasks to local specialized models, executes sandboxed code and local tools, verifies deliverables, and produces auditable outputs.

---

## Target Models & Hardware

Configured for local inference on an **NVIDIA GeForce RTX 4050 (6GB VRAM)**:

| Task Class | Model | Role |
|---|---|---|
| **Coding** | `Qwen2.5-Coder-3B` | Code generation, test synthesis, automated error repair |
| **Reasoning / General** | `Qwen3-4B` | Task planning, SOP analysis, multi-step agent reasoning |
| **Vision / Multimodal** | `Gemma 3 4B` | Scanned document OCR, P&ID visual inspection, image analysis |

---

## Repository Structure

```text
sovai/
├── frontend/              # Vite + React workbench UI
├── backend/               # FastAPI backend application
│   └── app/
│       ├── core/          # Settings & system configuration
│       ├── api/           # API routes & health telemetry
│       ├── agent/         # Stateful agent loop orchestrator (Phase 4)
│       ├── router/        # Capability-based task router (Phase 3)
│       ├── models/        # Model provider abstractions (Phases 1-2)
│       ├── tools/         # Tool registry & permission guard (Phase 5)
│       ├── sandbox/       # Zero-network Python sandbox (Phase 6)
│       ├── rag/           # Local knowledge base & embeddings (Phase 7)
│       ├── multimodal/    # OCR & vision pipeline (Phase 8)
│       ├── artifacts/     # Deterministic DOCX/XLSX/PPTX generators (Phase 9)
│       ├── verification/  # Multi-layer output verification engine (Phase 10)
│       ├── security/      # Network telemetry & audit logger (Phase 12)
│       └── services/      # Shared application services
├── docs/                  # Architecture & living roadmap
│   ├── ROADMAP.md         # Living roadmap tracking Phases 0–18
│   ├── PHASE_LOG.md       # Immutable phase completion changelog
│   └── architecture/      # Architecture specifications
├── models/                # Local model configurations
├── knowledge_base/        # Local industrial document corpus
├── sandbox/               # Isolated sandbox execution directory
├── data/                  # Artifact outputs and audit logs
├── deployment/            # Offline deployment manifests
├── security/              # Firewall rules and socket monitoring policies
├── scripts/               # Operational utility scripts
├── tests/                 # Comprehensive test suite (unit, integration, security, e2e)
├── .env.example           # Documented configuration variables
└── README.md              # Project documentation
```

---

## Quickstart & Local Development

### 1. Prerequisites
* **Python**: 3.12+ (installed natively or via WSL2)
* **Node.js**: 20+ & npm (installed natively or via WSL2)
* **Local Inference Runtime**: Ollama or vLLM running on `http://localhost:11434` with the target models pulled.

### 2. Environment Setup
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

### 3. Backend Setup & Run
```powershell
# Install backend dependencies
python -m pip install -r backend/requirements.txt

# Start FastAPI development server
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`  
Health Endpoint: `http://127.0.0.1:8000/api/health`

### 4. Frontend Setup & Run
```powershell
cd frontend
npm install
npm run dev
```
Access the Workbench at: `http://127.0.0.1:5173`

### 5. Running Automated Tests
```powershell
# Run unit tests
python -m pytest tests/unit -v

# Run entire test suite
python -m pytest tests -v
```

---

## Engineering Rules
SovAI strictly adheres to zero-hallucination engineering:
1. **Rule 1 — Do not hallucinate**: Never report a feature or test as passing unless verified with actual automated tests.
2. **Rule 2 — Work phase-by-phase**: Foundation before expansion.
3. **Rule 3 & 4 — Living Roadmap & Phase Log**: Maintained at `docs/ROADMAP.md` and `docs/PHASE_LOG.md`.
4. **Rule 7 — Do not over-engineer**: Minimal, robust architectures over premature complexity.
5. **Rule 8 — Verify before expanding**: Verify each phase with tests before moving forward.
