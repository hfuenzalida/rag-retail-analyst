"""Security-aware routing advisor."""

from app.models.query_models import QueryRequest
from app.models.routing import RoutingDecisionResult
from app.tools.routing_tools import check_sensitivity, log_routing_decision, resolve_routing_decision


def evaluate_routing(request: QueryRequest) -> RoutingDecisionResult:
    sensitivity = check_sensitivity(request.question)
    return log_routing_decision(resolve_routing_decision(request, sensitivity))
