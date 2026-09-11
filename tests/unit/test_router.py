import pytest
from backend.app.router.router_schema import TaskType, RoutingRequest, RoutingDecision
from backend.app.router.task_router import TaskRouter
from backend.app.models.registry import (
    ModelRegistry,
    ModelMetadata,
    ModelCategory,
    ModelStatus,
    ModelCapabilitiesInfo
)


@pytest.fixture
def mock_registry():
    registry = ModelRegistry()
    registry.register_model(ModelMetadata(
        id="qwen2.5-coder-3b",
        name="Qwen2.5-Coder-3B",
        type=ModelCategory.CODING,
        provider="ollama",
        endpoint="http://127.0.0.1:11434",
        tag="qwen2.5-coder:3b",
        capabilities=ModelCapabilitiesInfo(supports_vision=False, supports_tools=True),
        status=ModelStatus.AVAILABLE
    ))
    registry.register_model(ModelMetadata(
        id="qwen3-4b",
        name="Qwen3-4B",
        type=ModelCategory.REASONING,
        provider="ollama",
        endpoint="http://127.0.0.1:11434",
        tag="qwen3:4b",
        capabilities=ModelCapabilitiesInfo(supports_vision=False, supports_tools=True, supports_thinking=True),
        status=ModelStatus.AVAILABLE
    ))
    registry.register_model(ModelMetadata(
        id="gemma3-4b",
        name="Gemma 3 4B",
        type=ModelCategory.VISION,
        provider="ollama",
        endpoint="http://127.0.0.1:11434",
        tag="gemma3:4b",
        capabilities=ModelCapabilitiesInfo(supports_vision=True, supports_tools=False),
        status=ModelStatus.AVAILABLE
    ))
    return registry


def test_coding_request_routes_to_qwen25_coder(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    req = RoutingRequest(prompt="Write a Python script with a function def quicksort(arr): that sorts numbers.")
    decision = router.route(req)

    assert decision.task_type == TaskType.CODING
    assert decision.model_id == "qwen2.5-coder-3b"
    assert decision.model_tag == "qwen2.5-coder:3b"
    assert "python_sandbox" in decision.tools
    assert decision.confidence >= 0.70
    assert decision.fallback_used is False
    assert decision.clarification_needed is False


def test_reasoning_request_routes_to_qwen3(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    req = RoutingRequest(prompt="Analyze the safety SOP and evaluate the risk assessment step-by-step for turbine failure.")
    decision = router.route(req)

    assert decision.task_type == TaskType.REASONING
    assert decision.model_id == "qwen3-4b"
    assert decision.model_tag == "qwen3:4b"
    assert "search_documents" in decision.tools
    assert decision.confidence >= 0.70
    assert decision.fallback_used is False


def test_vision_request_routes_to_gemma3_multimodal(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    req = RoutingRequest(prompt="Inspect this scanned engineering drawing and analyze the P&ID piping layout.")
    decision = router.route(req)

    assert decision.task_type == TaskType.VISION
    assert decision.model_id == "gemma3-4b"
    assert decision.model_tag == "gemma3:4b"
    assert "analyze_image" in decision.tools
    assert decision.confidence >= 0.70
    assert decision.fallback_used is False


def test_file_attachment_triggers_vision_or_code(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    
    # Image file attached
    img_req = RoutingRequest(prompt="Inspect document", files=["valve_schematic.png"])
    img_decision = router.route(img_req)
    assert img_decision.task_type == TaskType.VISION
    assert img_decision.model_id == "gemma3-4b"

    # Code file attached
    code_req = RoutingRequest(prompt="Review implementation", files=["data_parser.py"])
    code_decision = router.route(code_req)
    assert code_decision.task_type == TaskType.CODING
    assert code_decision.model_id == "qwen2.5-coder-3b"


def test_ambiguous_request_produces_clarification_path(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    req = RoutingRequest(prompt="hello")
    decision = router.route(req)

    assert decision.task_type == TaskType.AMBIGUOUS
    assert decision.clarification_needed is True
    assert decision.clarification_prompt is not None
    assert "clarify" in decision.clarification_prompt.lower()


def test_router_never_selects_unavailable_model():
    # Setup registry where coding model is UNAVAILABLE
    offline_registry = ModelRegistry()
    offline_registry.register_model(ModelMetadata(
        id="qwen2.5-coder-3b",
        name="Qwen2.5-Coder-3B",
        type=ModelCategory.CODING,
        tag="qwen2.5-coder:3b",
        capabilities=ModelCapabilitiesInfo(supports_tools=True),
        status=ModelStatus.UNAVAILABLE  # Explicitly offline
    ))
    offline_registry.register_model(ModelMetadata(
        id="qwen3-4b",
        name="Qwen3-4B",
        type=ModelCategory.REASONING,
        tag="qwen3:4b",
        capabilities=ModelCapabilitiesInfo(supports_tools=True),
        status=ModelStatus.AVAILABLE
    ))

    router = TaskRouter(registry=offline_registry, audit_log_path=None)
    req = RoutingRequest(prompt="Implement a binary search tree in Python.")
    decision = router.route(req)

    # Must NOT route to the unavailable qwen2.5-coder-3b
    assert decision.model_id != "qwen2.5-coder-3b"
    assert decision.model_id == "qwen3-4b"
    assert decision.fallback_used is True


def test_at_least_two_task_classes_route_to_different_models(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    decision_coding = router.route(RoutingRequest(prompt="Write python code to compute prime numbers."))
    decision_reasoning = router.route(RoutingRequest(prompt="Deduce the root cause according to SOP guideline."))

    assert decision_coding.model_id != decision_reasoning.model_id
    assert decision_coding.model_id == "qwen2.5-coder-3b"
    assert decision_reasoning.model_id == "qwen3-4b"


def test_routing_decision_logged_in_history(mock_registry):
    router = TaskRouter(registry=mock_registry, audit_log_path=None)
    assert len(router.get_history()) == 0

    req = RoutingRequest(prompt="def calculate_total(): return 42")
    decision = router.route(req)

    history = router.get_history()
    assert len(history) == 1
    assert history[0].task_type == TaskType.CODING
    assert history[0].timestamp == decision.timestamp
