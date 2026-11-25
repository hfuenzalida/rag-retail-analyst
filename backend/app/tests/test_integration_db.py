"""Integration tests against PostgreSQL (optional — requires running DB)."""

import os
from datetime import date
from decimal import Decimal

import pytest

from app.core.config import Settings
from app.db.connection import close_pool, get_connection, init_pool
from app.db.repository import fetch_total_revenue, fetch_top_drivers
from app.db.seed.demo_retail import EXPECTED, seed_demo_retail
from app.models.query_models import DateRange, QueryFilters
from app.tools.metrics_tools import get_top_drivers as tool_get_top_drivers
from app.tools.metrics_tools import run_metric_query

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Set RUN_DB_INTEGRATION=1 with PostgreSQL running to execute",
)


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    settings = Settings(
        db_url=__import__("pydantic").SecretStr(
            os.getenv("APP_DB_URL", "postgresql://postgres:postgres@localhost:5432/rag_analyst")
        )
    )
    close_pool()
    init_pool(settings)
    with get_connection(settings) as conn:
        seed_demo_retail(conn)
    yield
    close_pool()


def test_seed_total_revenue_may_2026(seeded_db):
    settings = Settings(
        db_url=__import__("pydantic").SecretStr(
            os.getenv("APP_DB_URL", "postgresql://postgres:postgres@localhost:5432/rag_analyst")
        )
    )
    with get_connection(settings) as conn:
        filters = QueryFilters(
            date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
        )
        value = fetch_total_revenue(conn, "demo-retail", filters)
    assert value == Decimal(str(EXPECTED["may_2026_total_revenue"]))


def test_tool_total_revenue_may_2026(seeded_db):
    filters = QueryFilters(
        date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    )
    result = run_metric_query("total_revenue", "demo-retail", "manager", filters)
    assert result.value == Decimal("1640")


def test_tool_stock_out_rate(seeded_db):
    result = run_metric_query("stock_out_rate", "demo-retail", "manager")
    assert result.value == Decimal("33.33")


def test_category_drivers_may_vs_april(seeded_db):
    window = DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    drivers = tool_get_top_drivers("total_revenue", "category", window, "demo-retail", "analyst")
    assert drivers[0].dimension_value == "Shoes"
    assert drivers[0].impact == Decimal("-1260")
