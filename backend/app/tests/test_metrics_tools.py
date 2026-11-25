"""Metric tools tests with mocked database layer."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.query_models import DateRange, QueryFilters
from app.tools.metrics_tools import get_top_drivers, run_metric_query
from app.tools.rbac import PermissionDeniedError


@patch("app.tools.metrics_tools.fetch_total_revenue", return_value=Decimal("1640"))
@patch("app.tools.metrics_tools.get_connection")
def test_run_metric_query_total_revenue(mock_conn, mock_fetch):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None

    filters = QueryFilters(
        date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    )
    result = run_metric_query("total_revenue", "demo-retail", "manager", filters)
    assert result.name == "total_revenue"
    assert result.value == Decimal("1640")
    assert result.unit == "currency"
    mock_fetch.assert_called_once()


@patch("app.tools.metrics_tools.fetch_stock_out_rate", return_value=Decimal("33.33"))
@patch("app.tools.metrics_tools.get_connection")
def test_run_metric_query_stock_out_rate(mock_conn, mock_fetch):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None

    result = run_metric_query("stock_out_rate", "demo-retail", "manager")
    assert result.value == Decimal("33.33")
    assert result.time_window is None


@patch("app.tools.metrics_tools.fetch_gross_margin_pct", return_value=None)
@patch("app.tools.metrics_tools.get_connection")
def test_run_metric_query_margin_no_data(mock_conn, mock_fetch):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None

    with pytest.raises(ValueError, match="Insufficient data"):
        run_metric_query("gross_margin_pct", "demo-retail", "analyst")


@patch("app.tools.metrics_tools.fetch_top_drivers")
@patch("app.tools.metrics_tools.get_connection")
def test_get_top_drivers_delegates_to_repository(mock_conn, mock_drivers):
    from app.models.metrics import DriverResult

    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None
    mock_drivers.return_value = [
        DriverResult(
            dimension="category",
            dimension_value="Shoes",
            impact=Decimal("-1260"),
            current_value=Decimal("940"),
            prior_value=Decimal("2200"),
            description="test",
        )
    ]
    window = DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    drivers = get_top_drivers("total_revenue", "category", window, "demo-retail", "manager")
    assert drivers[0].impact == Decimal("-1260")


def test_get_top_drivers_rejects_unsupported_metric():
    window = DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    with pytest.raises(ValueError, match="not supported"):
        get_top_drivers("stock_out_rate", "category", window, "demo-retail", "analyst")
