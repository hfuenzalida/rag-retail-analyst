"""Data access for retail metrics and driver analysis."""

from decimal import Decimal

from psycopg import Connection

from app.db.filters import inventory_filters, prior_window, sales_filters
from app.models.metrics import DriverResult
from app.models.query_models import DateRange, QueryFilters

DIMENSION_COLUMNS = {
    "category": ("p.category", "JOIN products p ON s.sku = p.sku AND s.client_id = p.client_id"),
    "store_id": ("s.store_id", ""),
    "sku": ("s.sku", ""),
    "channel": ("s.channel", ""),
}


def _decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def fetch_total_revenue(
    conn: Connection,
    client_id: str,
    filters: QueryFilters | None,
) -> Decimal:
    sf = sales_filters(client_id, filters)
    sql = f"SELECT COALESCE(SUM(net_revenue), 0) AS value FROM sales s WHERE {sf.clause}"
    row = conn.execute(sql, sf.params).fetchone()
    return _decimal(row["value"])


def fetch_units_sold(
    conn: Connection,
    client_id: str,
    filters: QueryFilters | None,
) -> Decimal:
    sf = sales_filters(client_id, filters)
    sql = f"SELECT COALESCE(SUM(quantity), 0) AS value FROM sales s WHERE {sf.clause}"
    row = conn.execute(sql, sf.params).fetchone()
    return _decimal(row["value"])


def fetch_gross_margin_pct(
    conn: Connection,
    client_id: str,
    filters: QueryFilters | None,
) -> Decimal | None:
    sf = sales_filters(client_id, filters)
    sql = f"""
        SELECT
            COALESCE(SUM(s.net_revenue), 0) AS revenue,
            COALESCE(SUM(s.quantity * p.unit_cost), 0) AS cost
        FROM sales s
        JOIN products p ON s.sku = p.sku AND s.client_id = p.client_id
        WHERE {sf.clause}
    """
    row = conn.execute(sql, sf.params).fetchone()
    revenue = _decimal(row["revenue"])
    if revenue == 0:
        return None
    cost = _decimal(row["cost"])
    return ((revenue - cost) / revenue * 100).quantize(Decimal("0.01"))


def fetch_stock_out_rate(
    conn: Connection,
    client_id: str,
    filters: QueryFilters | None,
) -> Decimal | None:
    inv = inventory_filters(client_id, filters)
    sql = f"""
        SELECT
            COUNT(*) FILTER (WHERE on_hand_qty <= 0) AS out_count,
            COUNT(*) AS total_count
        FROM inventory i
        WHERE {inv.clause}
    """
    row = conn.execute(sql, inv.params).fetchone()
    total = int(row["total_count"])
    if total == 0:
        return None
    out_count = int(row["out_count"])
    return (Decimal(out_count) / Decimal(total) * 100).quantize(Decimal("0.01"))


def _metric_by_dimension(
    conn: Connection,
    client_id: str,
    dimension: str,
    window: DateRange,
    filters: QueryFilters | None,
    metric: str,
) -> dict[str, Decimal]:
    merged = QueryFilters(
        date_range=window,
        store_id=filters.store_id if filters else None,
        category=filters.category if filters else None,
        sku=filters.sku if filters else None,
    )
    sf = sales_filters(client_id, merged)
    dim_expr, join_clause = DIMENSION_COLUMNS[dimension]

    if metric == "total_revenue":
        agg = "COALESCE(SUM(s.net_revenue), 0)"
    elif metric == "units_sold":
        agg = "COALESCE(SUM(s.quantity), 0)"
    else:
        raise ValueError(f"Unsupported driver metric: {metric}")

    sql = f"""
        SELECT {dim_expr} AS dim_value, {agg} AS metric_value
        FROM sales s
        {join_clause}
        WHERE {sf.clause}
        GROUP BY {dim_expr}
        HAVING {dim_expr} IS NOT NULL
    """
    rows = conn.execute(sql, sf.params).fetchall()
    return {str(row["dim_value"]): _decimal(row["metric_value"]) for row in rows}


def fetch_top_drivers(
    conn: Connection,
    client_id: str,
    metric_name: str,
    dimension: str,
    window: DateRange,
    filters: QueryFilters | None,
    limit: int = 5,
) -> list[DriverResult]:
    if dimension not in DIMENSION_COLUMNS:
        raise ValueError(f"Unsupported dimension: {dimension}")

    prior = prior_window(window)
    current = _metric_by_dimension(conn, client_id, dimension, window, filters, metric_name)
    previous = _metric_by_dimension(conn, client_id, dimension, prior, filters, metric_name)

    keys = set(current) | set(previous)
    drivers: list[DriverResult] = []
    for key in keys:
        cur = current.get(key, Decimal("0"))
        prev = previous.get(key, Decimal("0"))
        impact = cur - prev
        if impact == 0:
            continue
        direction = "increased" if impact > 0 else "decreased"
        drivers.append(
            DriverResult(
                dimension=dimension,
                dimension_value=key,
                impact=impact,
                current_value=cur,
                prior_value=prev,
                description=(
                    f"{dimension} '{key}' {direction} by {abs(impact)} "
                    f"({prev} → {cur}) for {metric_name.replace('_', ' ')}."
                ),
            )
        )

    drivers.sort(key=lambda d: abs(d.impact), reverse=True)
    return drivers[:limit]
