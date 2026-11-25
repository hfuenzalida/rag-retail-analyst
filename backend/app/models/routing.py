"""Routing and sensitivity models."""

from typing import Literal

from pydantic import BaseModel, Field

SensitivityLevel = Literal["low", "medium", "high"]
RoutingDecision = Literal["local_only", "cloud_assist", "cloud_only"]


class SensitivityResult(BaseModel):
    level: SensitivityLevel
    reasons: list[str] = Field(default_factory=list)


class RoutingDecisionResult(BaseModel):
    sensitivity_level: SensitivityLevel
    routing_decision: RoutingDecision
    sanitization_required: bool
    cloud_provider_allowed: bool
    reasoning_summary: str
