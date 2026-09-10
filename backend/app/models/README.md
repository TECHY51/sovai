# Model Provider & Registry Subsystem

* **Target Phase**: Phase 1 (Provider Abstraction) & Phase 2 (Model Registry)
* **Scope**:
  * Provides abstract `ModelProvider` interface (`generate`, `stream`, `health`, `capabilities`).
  * Connects to local runtime endpoints (e.g. Ollama/vLLM) hosting `Qwen2.5-Coder-3B`, `Qwen3-4B`, and `Gemma 3 4B`.
  * Centralizes verified model metadata and capability declarations.
* **Status**: PENDING (Phases 1 & 2)
