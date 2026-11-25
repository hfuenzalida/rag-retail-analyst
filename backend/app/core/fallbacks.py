"""Tiered LLM polish fallbacks and kill-switch aware degradation."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.runtime_controls import is_kill_switch_active
from app.llm.client import LocalLLMClient, LLMMessage, polish_summary
from app.llm.cloud_client import CloudLLMClient, sanitize_summary_payload
from app.models.routing import RoutingDecisionResult


def polish_with_fallback(
    question: str,
    draft_summary: str,
    routing: RoutingDecisionResult,
    settings: Settings | None = None,
) -> tuple[str, str | None]:
    """
    Apply summary polish with layered fallbacks:
    cloud_assist -> local LLM -> grounded draft.
    Returns (summary, fallback_layer) where fallback_layer is None when primary succeeded.
    """
    cfg = settings or get_settings()
    cloud_requested = routing.routing_decision == "cloud_assist" and routing.cloud_provider_allowed

    if cloud_requested and not is_kill_switch_active("cloud_routing", settings=cfg):
        if not is_kill_switch_active("openai_provider", settings=cfg):
            try:
                client = CloudLLMClient(cfg)
                if client.is_configured:
                    payload = sanitize_summary_payload(question, draft_summary)
                    prompt = (
                        "Rewrite this grounded retail analytics summary clearly. "
                        "Do not add numbers or facts.\n\n"
                        f"Question: {payload['question']}\nSummary: {payload['summary']}"
                    )
                    return client.chat(prompt), None
            except Exception:
                pass

        local_result = _try_local_polish(question, draft_summary, cfg)
        if local_result is not None:
            return local_result, "local"
        return draft_summary, "draft"

    if is_kill_switch_active("local_llm", settings=cfg):
        return draft_summary, "draft"

    local_result = _try_local_polish(question, draft_summary, cfg)
    if local_result is not None:
        return local_result, None
    return draft_summary, "draft"


def _try_local_polish(question: str, draft_summary: str, cfg: Settings) -> str | None:
    llm = LocalLLMClient(cfg)
    if not llm.is_configured:
        return None
    try:
        polished = polish_summary(question, draft_summary, cfg)
        return polished
    except Exception:
        return None


def llm_unavailable_response() -> dict:
    """Structured safe response when all LLM layers are unavailable."""
    return {
        "summary": (
            "Analytics data is available, but language polish is temporarily unavailable. "
            "Showing grounded metrics only."
        ),
        "error_code": "LLM_UNAVAILABLE",
    }
