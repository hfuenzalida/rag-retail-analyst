"""Routing tests with runtime controls."""

from app.core.runtime_controls import load_runtime_controls
from app.models.query_models import QueryRequest
from app.tools.routing_tools import check_sensitivity, resolve_routing_decision


def test_cloud_routing_disabled_by_default():
    controls = load_runtime_controls(force_reload=True)
    assert controls.feature_flags.get("cloud_routing") is False

    request = QueryRequest(
        question="Total revenue",
        client_id="demo-retail",
        routing_hint="cloud_assist",
    )
    sensitivity = check_sensitivity(request.question)
    routing = resolve_routing_decision(request, sensitivity)
    assert routing.routing_decision == "local_only"
