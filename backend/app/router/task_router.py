import re
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from backend.app.router.router_schema import TaskType, RoutingRequest, RoutingDecision
from backend.app.models.registry import ModelRegistry, ModelStatus, ModelCategory
from backend.app.models import get_model_registry

logger = logging.getLogger("sovai.router")

# Precompiled regex patterns for deterministic heuristic matching
CODING_PATTERNS = [
    re.compile(r"\b(def|class|import|return|lambda|yield|raise)\s+[a-zA-Z_]", re.IGNORECASE),
    re.compile(r"\b(python|script|function|algorithm|refactor|debug|bug|syntaxerror|pytest|unittest|traceback)\b", re.IGNORECASE),
    re.compile(r"\b(sandbox|execute code|run code|pip install|fastapi|asyncio|regex|json serialization)\b", re.IGNORECASE),
    re.compile(r"```[a-zA-Z]*\n", re.IGNORECASE),
]

VISION_PATTERNS = [
    re.compile(r"\b(p&id|pid|piping and instrumentation|schematic|blueprint|engineering drawing)\b", re.IGNORECASE),
    re.compile(r"\b(scanned|ocr|handwritten|handwriting|diagram|visual inspection|photo|image|picture)\b", re.IGNORECASE),
    re.compile(r"\b(inspect this image|analyze image|extract text from image|read scan)\b", re.IGNORECASE),
]

REASONING_PATTERNS = [
    re.compile(r"\b(sop|standard operating procedure|compliance|regulatory|incident report)\b", re.IGNORECASE),
    re.compile(r"\b(step-by-step|root cause|risk assessment|failure mode|deduce|evaluate|synthesize)\b", re.IGNORECASE),
    re.compile(r"\b(reasoning|why did|how should we handle|compare findings|safety check)\b", re.IGNORECASE),
]

IMAGE_FILE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".gif"}
DOCUMENT_FILE_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx"}
CODE_FILE_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".html", ".css", ".sql", ".json"}

DEFAULT_TOOLS: Dict[TaskType, List[str]] = {
    TaskType.CODING: ["python_sandbox", "read_file", "write_file"],
    TaskType.REASONING: ["search_documents", "calculate"],
    TaskType.VISION: ["ocr_document", "analyze_image"],
    TaskType.GENERAL: ["search_documents"],
    TaskType.AMBIGUOUS: [],
}

PREFERRED_MODELS: Dict[TaskType, str] = {
    TaskType.CODING: "qwen2.5-coder-3b",
    TaskType.REASONING: "qwen3-4b",
    TaskType.VISION: "gemma3-4b",
    TaskType.GENERAL: "qwen3-4b",
}


class TaskRouter:
    def __init__(self, registry: Optional[ModelRegistry] = None, audit_log_path: Optional[str] = "data/logs/routing_audit.jsonl"):
        self._registry = registry or get_model_registry()
        self._audit_log_path = Path(audit_log_path) if audit_log_path else None
        self._history: List[RoutingDecision] = []

    def classify_task(self, request: RoutingRequest) -> Tuple[TaskType, float, str]:
        # Explicit operator hint overrides heuristic detection
        if request.task_type_hint:
            return request.task_type_hint, 1.0, f"Explicit operator hint provided: '{request.task_type_hint.value}'."

        prompt_text = request.prompt.strip()

        # Check attached file extensions
        if request.files:
            for file_ref in request.files:
                ext = Path(file_ref).suffix.lower()
                if ext in IMAGE_FILE_EXTENSIONS:
                    return TaskType.VISION, 0.95, f"Attached image file detected: '{file_ref}'."
                if ext in CODE_FILE_EXTENSIONS:
                    return TaskType.CODING, 0.95, f"Attached code source file detected: '{file_ref}'."

        if not prompt_text:
            return TaskType.AMBIGUOUS, 0.1, "Prompt is empty; cannot determine task classification."

        coding_score = sum(1 for p in CODING_PATTERNS if p.search(prompt_text))
        vision_score = sum(1 for p in VISION_PATTERNS if p.search(prompt_text))
        reasoning_score = sum(1 for p in REASONING_PATTERNS if p.search(prompt_text))

        # Check for vision/multimodal indicators
        if vision_score > 0 and vision_score >= coding_score and vision_score >= reasoning_score:
            confidence = min(0.70 + (vision_score * 0.10), 0.98)
            return TaskType.VISION, confidence, "Detected visual, OCR, or engineering diagram keywords."

        # Check for coding indicators
        if coding_score > 0 and coding_score >= reasoning_score:
            confidence = min(0.70 + (coding_score * 0.10), 0.98)
            return TaskType.CODING, confidence, "Detected code structure, syntax patterns, or script keywords."

        # Check for reasoning / SOP indicators
        if reasoning_score > 0:
            confidence = min(0.70 + (reasoning_score * 0.10), 0.98)
            return TaskType.REASONING, confidence, "Detected industrial reasoning, SOP, or analytical planning patterns."

        # Very short or conversational query
        if len(prompt_text.split()) < 3 and not (coding_score or vision_score or reasoning_score):
            return TaskType.AMBIGUOUS, 0.35, "Query is too brief or ambiguous for deterministic task routing."

        # Fallback to general reasoning
        return TaskType.GENERAL, 0.60, "No specialized task cues identified; routed to general reasoning model."

    def route(self, request: RoutingRequest) -> RoutingDecision:
        task_type, confidence, classification_reason = self.classify_task(request)

        # Handle ambiguous queries
        if task_type == TaskType.AMBIGUOUS:
            # Check if general model is available to handle clarification
            preferred_id = PREFERRED_MODELS[TaskType.GENERAL]
            target_model = self._select_available_model(preferred_id, TaskType.GENERAL)
            
            decision = RoutingDecision(
                task_type=TaskType.AMBIGUOUS,
                model_id=target_model.id if target_model else "none",
                model_tag=target_model.tag if target_model else "none",
                tools=[],
                confidence=confidence,
                reasoning=classification_reason,
                fallback_used=True,
                clarification_needed=True,
                clarification_prompt="Could you clarify if your task involves coding, industrial reasoning/SOP analysis, or document/image inspection?"
            )
            self._record_decision(decision, request)
            return decision

        preferred_id = PREFERRED_MODELS.get(task_type, PREFERRED_MODELS[TaskType.GENERAL])
        target_model = self._select_available_model(preferred_id, task_type)

        fallback_used = False
        tools = list(DEFAULT_TOOLS.get(task_type, []))

        if target_model is None:
            # Preferred model is unavailable, search for any available model in registry
            available_models = self._registry.get_available_models()
            if not available_models:
                # No models are available in the entire registry
                decision = RoutingDecision(
                    task_type=task_type,
                    model_id="none",
                    model_tag="none",
                    tools=[],
                    confidence=0.0,
                    reasoning=f"Preferred model '{preferred_id}' and all fallback models are UNAVAILABLE.",
                    fallback_used=True,
                    clarification_needed=True,
                    clarification_prompt="All local models are currently unavailable. Please verify local inference runtime."
                )
                self._record_decision(decision, request)
                return decision

            # For vision tasks, only select a model that actually supports vision
            if task_type == TaskType.VISION:
                vision_models = [m for m in available_models if m.capabilities.supports_vision]
                if vision_models:
                    target_model = vision_models[0]
                    fallback_used = True
                else:
                    # No vision model available; fallback to general with warning
                    target_model = available_models[0]
                    fallback_used = True
                    tools = ["ocr_document"]  # Fallback to OCR text without raw vision
                    classification_reason += f" (Note: Preferred vision model '{preferred_id}' unavailable; routed to fallback '{target_model.id}' without native vision capabilities)."
            else:
                target_model = available_models[0]
                fallback_used = True
                classification_reason += f" (Note: Preferred model '{preferred_id}' unavailable; routed to available fallback model '{target_model.id}')."

        decision = RoutingDecision(
            task_type=task_type,
            model_id=target_model.id,
            model_tag=target_model.tag,
            tools=tools,
            confidence=confidence,
            reasoning=classification_reason,
            fallback_used=fallback_used,
            clarification_needed=False
        )

        self._record_decision(decision, request)
        return decision

    def _select_available_model(self, model_id: str, required_task: TaskType):
        model = self._registry.get_model(model_id)
        if model and model.status == ModelStatus.AVAILABLE:
            if required_task == TaskType.VISION and not model.capabilities.supports_vision:
                return None
            return model
        return None

    def _record_decision(self, decision: RoutingDecision, request: RoutingRequest) -> None:
        self._history.append(decision)
        if len(self._history) > 100:
            self._history.pop(0)

        log_payload = {
            "timestamp": decision.timestamp,
            "task_type": decision.task_type.value,
            "model_id": decision.model_id,
            "confidence": decision.confidence,
            "fallback_used": decision.fallback_used,
            "prompt_sample": request.prompt[:120],
            "reasoning": decision.reasoning
        }

        logger.info(f"Task Routed: {log_payload}")

        if self._audit_log_path:
            try:
                self._audit_log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._audit_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_payload) + "\n")
            except Exception as exc:
                logger.warning(f"Could not write routing audit log: {exc}")

    def get_history(self) -> List[RoutingDecision]:
        return list(self._history)
