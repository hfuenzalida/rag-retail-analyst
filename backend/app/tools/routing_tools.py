"""Sensitivity classification and routing decision tools."""

import re

from app.core.config import Settings, get_settings
from app.core.rollout import is_feature_available_for_role
from app.core.runtime_controls import cloud_routing_allowed
from app.models.query_models import QueryRequest
from app.models.routing import RoutingDecision, RoutingDecisionResult, SensitivityLevel, SensitivityResult

HIGH_SENSITIVITY_PATTERNS = [
    r"\bcustomer\b",
    r"\bpatient\b",
    r"\bsalary\b",
    r"\bssn\b",
    r"\bcredit card\b",
    r"\bpii\b",
]

MEDIUM_SENSITIVITY_PATTERNS = [
    r"\btransaction id\b",
    r"\border id\b",
    r"\bemail\b",
    r"\bphone\b",
]


def check_sensitivity(prompt: str, context_summary: str | None = None) -> SensitivityResult:
    """Classify prompt sensitivity before any cloud LLM call."""
    text = f"{prompt} {context_summary or ''}".lower()
    reasons: list[str] = []

    for pattern in HIGH_SENSITIVITY_PATTERNS:
        if re.search(pattern, text):
            reasons.append(f"Matched high-sensitivity pattern: {pattern}")

    if reasons:
        return SensitivityResult(level="high", reasons=reasons)

    for pattern in MEDIUM_SENSITIVITY_PATTERNS:
        if re.search(pattern, text):
            reasons.append(f"Matched medium-sensitivity pattern: {pattern}")

    if reasons:
        return SensitivityResult(level="medium", reasons=reasons)

    return SensitivityResult(level="low", reasons=["No sensitive markers detected"])


def resolve_routing_decision(
    request: QueryRequest,
    sensitivity: SensitivityResult,
    settings: Settings | None = None,
) -> RoutingDecisionResult:
    """Decide local vs cloud execution path."""
    cfg = settings or get_settings()

    if request.routing_hint == "local_only":
        return RoutingDecisionResult(
            sensitivity_level=sensitivity.level,
            routing_decision="local_only",
            sanitization_required=False,
            cloud_provider_allowed=False,
            reasoning_summary="Client forced local_only routing.",
        )

    if sensitivity.level == "high":
        return RoutingDecisionResult(
            sensitivity_level="high",
            routing_decision="local_only",
            sanitization_required=False,
            cloud_provider_allowed=False,
            reasoning_summary="High sensitivity content must stay on local infrastructure.",
        )

    cloud_enabled = cloud_routing_allowed(cfg) and any(
        [
            cfg.enable_openai and cfg.openai_api_key,
            cfg.enable_anthropic and cfg.anthropic_api_key,
            cfg.enable_gemini and cfg.gemini_api_key,
        ]
    )

    if request.routing_hint == "cloud_assist" and cloud_enabled and sensitivity.level == "low":
        if not is_feature_available_for_role("cloud_routing", request.role):
            return RoutingDecisionResult(
                sensitivity_level=sensitivity.level,
                routing_decision="local_only",
                sanitization_required=False,
                cloud_provider_allowed=False,
                reasoning_summary="Cloud routing not enabled for this role in current rollout.",
            )
        return RoutingDecisionResult(
            sensitivity_level=sensitivity.level,
            routing_decision="cloud_assist",
            sanitization_required=True,
            cloud_provider_allowed=True,
            reasoning_summary="Low sensitivity with explicit cloud_assist hint.",
        )

    if sensitivity.level == "medium":
        return RoutingDecisionResult(
            sensitivity_level="medium",
            routing_decision="local_only",
            sanitization_required=True,
            cloud_provider_allowed=cloud_enabled,
            reasoning_summary="Medium sensitivity — local execution with sanitization if cloud is used.",
        )

    return RoutingDecisionResult(
        sensitivity_level=sensitivity.level,
        routing_decision="local_only",
        sanitization_required=False,
        cloud_provider_allowed=cloud_enabled,
        reasoning_summary="Default sovereign local routing for business analytics.",
    )


def log_routing_decision(result: RoutingDecisionResult) -> RoutingDecisionResult:
    """Pass-through hook reserved for observability integrations."""
    return result


def sanitize_for_cloud(text: str) -> str:
    from app.llm.cloud_client import sanitize_text

    return sanitize_text(text)


def route_to_cloud_llm(task_description: str, sanitized_payload: dict, settings: Settings | None = None) -> str:
    """Send sanitized payload to configured cloud LLM provider."""
    cfg = settings or get_settings()
    from app.llm.cloud_client import CloudLLMClient

    client = CloudLLMClient(cfg)
    prompt = f"{task_description}\n\nPayload:\n{sanitized_payload}"
    return client.chat(prompt)
