"""Metric tool result models."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.models.query_models import DateRange, Driver, QueryFilters

Role = Literal["manager", "analyst", "admin"]

CANONICAL_METRICS = frozenset(
    {"total_revenue", "units_sold", "stock_out_rate", "gross_margin_pct"}
)

DRIVER_DIMENSIONS = frozenset({"category", "store_id", "sku", "channel"})

# Managers may not access margin metrics (financial sensitivity).
METRICS_BY_ROLE: dict[Role, frozenset[str]] = {
    "manager": frozenset({"total_revenue", "units_sold", "stock_out_rate"}),
    "analyst": CANONICAL_METRICS,
    "admin": CANONICAL_METRICS,
}


class MetricResult(BaseModel):
    name: str
    value: Decimal
    unit: str | None = None
    time_window: DateRange | None = None
    context: str | None = None


class DriverResult(BaseModel):
    dimension: str
    dimension_value: str
    impact: Decimal
    current_value: Decimal
    prior_value: Decimal
    description: str

    def to_driver(self) -> Driver:
        return Driver(
            dimension=f"{self.dimension}:{self.dimension_value}",
            impact=self.impact,
            description=self.description,
        )


class MetricToolContext(BaseModel):
    client_id: str
    role: Role
    filters: QueryFilters | None = None
