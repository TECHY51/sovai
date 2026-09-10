# SovAI — System Architecture Overview

## 1. High-Level Architecture

SovAI implements a decoupled, local-first architecture ensuring zero leakage of confidential industrial data:

```text
┌─────────────────────────────────────────────────────────┐
│                    Web Workbench UI                     │
│    (Chat, Tasks, Knowledge, Models, Artifacts, Security)│
└────────────────────────────┬────────────────────────────┘
                             │ HTTP / SSE (/api)
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │               Agent Orchestrator                │   │
│   │  (Understand → Plan → Route → Act → Verify)     │   │
│   └────────┬───────────────────────────────┬────────┘   │
│            │                               │            │
│            ▼                               ▼            │
│   ┌─────────────────┐             ┌─────────────────┐   │
│   │   Task Router   │             │  Tool Registry  │   │
│   └────────┬────────┘             └────────┬────────┘   │
│            │                               │            │
│            ▼                               ▼            │
│   ┌─────────────────┐             ┌─────────────────┐   │
│   │ Model Registry  │             │ Execution Tools │   │
│   └────────┬────────┘             │ - Sandbox       │   │
│            │                      │ - RAG           │   │
│            ▼                      │ - Multimodal    │   │
│   ┌─────────────────┐             │ - Generators    │   │
│   │ Local Providers │             └────────┬────────┘   │
│   └────────┬────────┘                      │            │
│            │                               ▼            │
│            ▼                      ┌─────────────────┐   │
│   ┌─────────────────┐             │  Verification   │   │
│   │ RTX 4050 Models │             │     Engine      │   │
│   │ Qwen2.5-Coder-3B│             └────────┬────────┘   │
│   │ Qwen3-4B        │                      │            │
│   │ Gemma 3 4B      │                      ▼            │
│   └─────────────────┘             ┌─────────────────┐   │
│                                   │ Deliverable Doc │   │
│                                   └─────────────────┘   │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │           Security & Sovereignty Layer          │   │
│   │  (Air-Gap Enforcement, Outbound Socket Guard,   │   │
│   │   Audit Logging, Resource Boundaries)           │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2. Core Principles
1. **Air-Gap Strictness**: No runtime calls to public cloud LLM APIs (OpenAI, Anthropic, Google Cloud, etc.).
2. **Deterministic Tooling**: Complex deliverables (DOCX, XLSX, PPTX) and code execution are handled deterministically through specialized engines and sandboxes, not by unverified LLM raw output.
3. **Continuous Verification**: Results are independently tested and grounded before being delivered to the operator.
