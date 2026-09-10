import time
import json
import httpx
from typing import Optional, List, Dict, Any, AsyncIterator
from backend.app.models.base import (
    ModelProvider,
    ModelResponse,
    ProviderHealth,
    ModelCapabilities,
    ModelError
)


class OllamaProvider(ModelProvider):
    def __init__(self, endpoint: str = "http://127.0.0.1:11434", timeout_seconds: float = 120.0):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout_seconds

    async def health(self) -> ProviderHealth:
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.endpoint}/api/tags")
                elapsed_ms = (time.perf_counter() - start) * 1000
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return ProviderHealth(
                        provider="ollama",
                        endpoint=self.endpoint,
                        reachable=True,
                        latency_ms=round(elapsed_ms, 2),
                        installed_models=models
                    )
                return ProviderHealth(
                    provider="ollama",
                    endpoint=self.endpoint,
                    reachable=False,
                    latency_ms=round(elapsed_ms, 2),
                    error_message=f"HTTP {res.status_code}: {res.text}"
                )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return ProviderHealth(
                provider="ollama",
                endpoint=self.endpoint,
                reachable=False,
                latency_ms=round(elapsed_ms, 2),
                error_message=str(e)
            )

    async def capabilities(self, model: str) -> ModelCapabilities:
        health_info = await self.health()
        if not health_info.reachable:
            raise ModelError(f"Inference provider at {self.endpoint} is unreachable", status_code=503)

        # Query model information from Ollama
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.endpoint}/api/show", json={"name": model})
                if res.status_code != 200:
                    raise ModelError(
                        f"Model '{model}' is not available on provider. Install with 'ollama pull {model}'.",
                        status_code=404,
                        model=model
                    )
                info = res.json()
                
                # Check for verified vision capabilities
                details = info.get("details", {})
                families = details.get("families", []) or [details.get("family", "")]
                
                # Gemma 3 or explicit clip/vision architecture indicates verified multimodal capability
                is_vision = "gemma3" in model.lower() or "clip" in str(families).lower()
                
                context_len = 4096
                if "model_info" in info:
                    context_len = info["model_info"].get("general.context_length", 4096)

                return ModelCapabilities(
                    model=model,
                    supports_vision=is_vision,
                    supports_tools=True,
                    supports_streaming=True,
                    context_window=context_len,
                    verified=True,
                    details=details
                )
        except httpx.RequestError as exc:
            raise ModelError(f"Connection error reaching model server: {exc}", status_code=503, model=model)

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        images: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if images:
            payload["images"] = images
        if options:
            payload["options"] = options

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.endpoint}/api/generate", json=payload)
                elapsed_ms = (time.perf_counter() - start) * 1000

                if res.status_code == 404:
                    raise ModelError(f"Model '{model}' not found on provider.", status_code=404, model=model)
                if res.status_code != 200:
                    raise ModelError(f"Inference error ({res.status_code}): {res.text}", status_code=res.status_code, model=model)

                data = res.json()
                response_text = data.get("response", "")
                thinking_text = data.get("thinking")
                
                # If final response is empty because token limit was reached inside thinking phase,
                # provide the thinking output as content so the caller has actionable reasoning text.
                content_text = response_text if response_text else (thinking_text or "")

                return ModelResponse(
                    model=model,
                    content=content_text,
                    thinking=thinking_text,
                    tokens_prompt=data.get("prompt_eval_count"),
                    tokens_completion=data.get("eval_count"),
                    latency_ms=round(elapsed_ms, 2),
                    done=data.get("done", True)
                )
        except httpx.RequestError as exc:
            raise ModelError(f"Network error communicating with Ollama: {exc}", status_code=503, model=model)

    async def stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        images: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        if system:
            payload["system"] = system
        if images:
            payload["images"] = images
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.endpoint}/api/generate", json=payload) as response:
                    if response.status_code != 200:
                        err_body = await response.aread()
                        raise ModelError(f"Stream error ({response.status_code}): {err_body.decode()}", status_code=response.status_code, model=model)
                    
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        yield chunk.get("response", "")
        except httpx.RequestError as exc:
            raise ModelError(f"Stream connection failed: {exc}", status_code=503, model=model)
