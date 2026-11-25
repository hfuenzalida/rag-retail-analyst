"""Tiered LLM fallback tests."""

from unittest.mock import MagicMock, patch

from app.core.fallbacks import polish_with_fallback
from app.models.routing import RoutingDecisionResult


def _routing(decision: str = "local_only", cloud_allowed: bool = False) -> RoutingDecisionResult:
    return RoutingDecisionResult(
        sensitivity_level="low",
        routing_decision=decision,  # type: ignore[arg-type]
        sanitization_required=decision == "cloud_assist",
        cloud_provider_allowed=cloud_allowed,
        reasoning_summary="test",
    )


@patch("app.core.fallbacks.is_kill_switch_active", return_value=True)
def test_local_kill_switch_returns_draft(_kill):
    summary, layer = polish_with_fallback("Q?", "Draft metrics.", _routing())
    assert summary == "Draft metrics."
    assert layer == "draft"


@patch("app.core.fallbacks._try_local_polish", return_value="Polished local")
@patch("app.core.fallbacks.is_kill_switch_active", return_value=False)
def test_local_polish_succeeds(_kill, _local):
    summary, layer = polish_with_fallback("Q?", "Draft.", _routing())
    assert summary == "Polished local"
    assert layer is None


@patch("app.core.fallbacks._try_local_polish", return_value="Local fallback")
@patch("app.core.fallbacks.CloudLLMClient")
@patch("app.core.fallbacks.is_kill_switch_active", return_value=False)
def test_cloud_failure_falls_back_to_local(mock_kill, mock_client_cls, _local):
    instance = MagicMock()
    instance.is_configured = True
    instance.chat.side_effect = RuntimeError("cloud down")
    mock_client_cls.return_value = instance

    from app.core.config import Settings

    settings = Settings(enable_openai=True, openai_api_key="test-key")
    summary, layer = polish_with_fallback(
        "Q?",
        "Draft.",
        _routing("cloud_assist", cloud_allowed=True),
        settings,
    )
    assert summary == "Local fallback"
    assert layer == "local"


@patch("app.core.fallbacks._try_local_polish", return_value=None)
@patch("app.core.fallbacks.CloudLLMClient")
@patch("app.core.fallbacks.is_kill_switch_active", return_value=False)
def test_cloud_and_local_failure_returns_draft(mock_kill, mock_client_cls, _local):
    instance = MagicMock()
    instance.is_configured = True
    instance.chat.side_effect = RuntimeError("cloud down")
    mock_client_cls.return_value = instance

    from app.core.config import Settings

    settings = Settings(enable_openai=True, openai_api_key="test-key")
    summary, layer = polish_with_fallback(
        "Q?",
        "Grounded draft.",
        _routing("cloud_assist", cloud_allowed=True),
        settings,
    )
    assert summary == "Grounded draft."
    assert layer == "draft"
