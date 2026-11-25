"""Pre-defined metric computation tools (no raw SQL exposed to agents)."""

from datetime import date, timedelta

from app.db.connection import get_connection
from app.db.repository import (
    fetch_gross_margin_pct,
    fetch_stock_out_rate,
    fetch_top_drivers,
    fetch_total_revenue,
    fetch_units_sold,
)
from app.models.metrics import DRIVER_DIMENSIONS, DriverResult, MetricResult, Role
from app.models.query_models import DateRange, QueryFilters
from app.tools.rbac import assert_dimension_allowed, assert_metric_allowed

METRIC_UNITS = {
    "total_revenue": "currency",
    "units_sold": "units",
    "stock_out_rate": "percent",
    "gross_margin_pct": "percent",
}


def _default_date_range() -> DateRange:
    end = date.today()
    start = end - timedelta(days=30)
    return DateRange(start_date=start, end_date=end)


def _with_date_window(filters: QueryFilters | None, window: DateRange) -> QueryFilters:
    base = filters or QueryFilters()
    if base.date_range:
        return base
    return QueryFilters(
        date_range=window,
        store_id=base.store_id,
        category=base.category,
        sku=base.sku,
    )


def _context_label(filters: QueryFilters | None) -> str | None:
    if not filters:
        return None
    parts = []
    if filters.store_id:
        parts.append(f"store={filters.store_id}")
    if filters.category:
        parts.append(f"category={filters.category}")
    if filters.sku:
        parts.append(f"sku={filters.sku}")
    return ", ".join(parts) if parts else None


def run_metric_query(
    metric_name: str,
    client_id: str,
    role: Role,
    filters: QueryFilters | None = None,
) -> MetricResult:
    """Compute a vetted retail metric for the given client and filters."""
    assert_metric_allowed(metric_name, role)

    with get_connection() as conn:
        if metric_name == "total_revenue":
            window = _default_date_range()
            effective = _with_date_window(filters, window)
            value = fetch_total_revenue(conn, client_id, effective)
            time_window = effective.date_range
        elif metric_name == "units_sold":
            window = _default_date_range()
            effective = _with_date_window(filters, window)
            value = fetch_units_sold(conn, client_id, effective)
            time_window = effective.date_range
        elif metric_name == "gross_margin_pct":
            window = _default_date_range()
            effective = _with_date_window(filters, window)
            pct = fetch_gross_margin_pct(conn, client_id, effective)
            if pct is None:
                raise ValueError("Insufficient data to compute gross_margin_pct for the selected filters.")
            value = pct
            time_window = effective.date_range
        elif metric_name == "stock_out_rate":
            pct = fetch_stock_out_rate(conn, client_id, filters)
            if pct is None:
                raise ValueError("No inventory records found for the selected filters.")
            value = pct
            time_window = None
        else:
            raise ValueError(f"Unknown metric: {metric_name}")

    return MetricResult(
        name=metric_name,
        value=value,
        unit=METRIC_UNITS[metric_name],
        time_window=time_window,
        context=_context_label(filters),
    )


def get_top_drivers(
    metric_name: str,
    dimension: str,
    window: DateRange,
    client_id: str,
    role: Role,
    filters: QueryFilters | None = None,
    limit: int = 5,
) -> list[DriverResult]:
    """Rank dimension values by contribution to metric change vs prior period."""
    assert_metric_allowed(metric_name, role)
    assert_dimension_allowed(role)
    if dimension not in DRIVER_DIMENSIONS:
        raise ValueError(f"Unsupported dimension: {dimension}")
    if metric_name not in ("total_revenue", "units_sold"):
        raise ValueError(f"Driver analysis not supported for metric: {metric_name}")

    with get_connection() as conn:
        return fetch_top_drivers(
            conn,
            client_id=client_id,
            metric_name=metric_name,
            dimension=dimension,
            window=window,
            filters=filters,
            limit=limit,
        )
