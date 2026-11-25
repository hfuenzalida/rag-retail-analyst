"""Local vs cloud LLM routing logic."""

from app.models.routing import RoutingDecision

__all__ = ["RoutingDecision", "default_routing_decision"]


def default_routing_decision() -> RoutingDecision:
    return "local_only"
