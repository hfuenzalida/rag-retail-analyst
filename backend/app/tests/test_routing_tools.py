"""Routing and sensitivity tests."""

from app.models.query_models import QueryRequest
from app.tools.routing_tools import check_sensitivity, resolve_routing_decision


def test_check_sensitivity_high_for_customer():
    result = check_sensitivity("Show me customer John Smith purchase history")
    assert result.level == "high"
    assert result.reasons


def test_check_sensitivity_low_for_revenue():
    result = check_sensitivity("What was total revenue last month?")
    assert result.level == "low"


def test_resolve_routing_local_only_by_default():
    request = QueryRequest(question="Total revenue last week", client_id="demo-retail")
    sensitivity = check_sensitivity(request.question)
    routing = resolve_routing_decision(request, sensitivity)
    assert routing.routing_decision == "local_only"


def test_resolve_routing_respects_local_only_hint():
    request = QueryRequest(
        question="Total revenue",
        client_id="demo-retail",
        routing_hint="local_only",
    )
    sensitivity = check_sensitivity(request.question)
    routing = resolve_routing_decision(request, sensitivity)
    assert routing.routing_decision == "local_only"
    assert not routing.cloud_provider_allowed


def test_high_sensitivity_forces_local():
    request = QueryRequest(question="List customer emails and salary data", client_id="demo-retail")
    sensitivity = check_sensitivity(request.question)
    routing = resolve_routing_decision(request, sensitivity)
    assert routing.routing_decision == "local_only"
