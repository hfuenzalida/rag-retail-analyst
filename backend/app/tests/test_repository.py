"""Repository SQL unit tests with mocked connections."""

from decimal import Decimal
from unittest.mock import MagicMock

from app.db.repository import (
    fetch_gross_margin_pct,
    fetch_stock_out_rate,
    fetch_top_drivers,
    fetch_total_revenue,
    fetch_units_sold,
)
from app.models.query_models import DateRange, QueryFilters


def test_fetch_total_revenue():
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = {"value": Decimal("1640")}
    filters = QueryFilters(
        date_range=DateRange(start_date=__import__("datetime").date(2026, 5, 1), end_date=__import__("datetime").date(2026, 5, 31))
    )
    value = fetch_total_revenue(conn, "demo-retail", filters)
    assert value == Decimal("1640")
    sql = conn.execute.call_args[0][0]
    assert "SUM(net_revenue)" in sql
    assert "demo-retail" in conn.execute.call_args[0][1]


def test_fetch_units_sold():
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = {"value": 31}
    value = fetch_units_sold(conn, "demo-retail", None)
    assert value == Decimal("31")


def test_fetch_gross_margin_pct():
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = {"revenue": Decimal("1640"), "cost": Decimal("770")}
    pct = fetch_gross_margin_pct(conn, "demo-retail", None)
    assert pct == Decimal("53.05")


def test_fetch_gross_margin_pct_no_revenue():
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = {"revenue": Decimal("0"), "cost": Decimal("0")}
    assert fetch_gross_margin_pct(conn, "demo-retail", None) is None


def test_fetch_stock_out_rate():
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = {"out_count": 1, "total_count": 3}
    rate = fetch_stock_out_rate(conn, "demo-retail", None)
    assert rate == Decimal("33.33")


def test_fetch_top_drivers_ranks_by_impact():
    conn = MagicMock()
    current_result = MagicMock()
    current_result.fetchall.return_value = [
        {"dim_value": "Shoes", "metric_value": Decimal("940")},
        {"dim_value": "Apparel", "metric_value": Decimal("700")},
    ]
    prior_result = MagicMock()
    prior_result.fetchall.return_value = [
        {"dim_value": "Shoes", "metric_value": Decimal("2200")},
        {"dim_value": "Apparel", "metric_value": Decimal("875")},
    ]
    conn.execute.side_effect = [current_result, prior_result]

    window = DateRange(
        start_date=__import__("datetime").date(2026, 5, 1),
        end_date=__import__("datetime").date(2026, 5, 31),
    )
    drivers = fetch_top_drivers(
        conn,
        client_id="demo-retail",
        metric_name="total_revenue",
        dimension="category",
        window=window,
        filters=None,
    )
    assert drivers[0].dimension_value == "Shoes"
    assert drivers[0].impact == Decimal("-1260")
