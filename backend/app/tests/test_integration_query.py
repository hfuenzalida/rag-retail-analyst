"""Integration test for full query path against PostgreSQL."""

import os
from datetime import date

import pytest

from app.core.config import Settings
from app.db.connection import close_pool, get_connection, init_pool
from app.db.seed.demo_retail import seed_demo_retail
from app.models.query_models import DateRange, QueryFilters, QueryRequest
from app.services.query_pipeline import execute_query

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


def test_query_total_revenue_may_2026(seeded_db):
    request = QueryRequest(
        question="What was total net revenue last month?",
        client_id="demo-retail",
        role="manager",
        filters=QueryFilters(
            date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
        ),
    )
    response = execute_query(request, use_llm_polish=False)
    assert response.error is None
    assert response.metrics[0].name == "total_revenue"
    assert float(response.metrics[0].value) == 1640.0
    assert response.citations


def test_query_stock_out_rate(seeded_db):
    request = QueryRequest(
        question="Which SKUs are currently out of stock?",
        client_id="demo-retail",
        role="manager",
    )
    response = execute_query(request, use_llm_polish=False)
    assert any(m.name == "stock_out_rate" for m in response.metrics)


def test_query_category_drivers(seeded_db):
    request = QueryRequest(
        question="Why did revenue change by category?",
        client_id="demo-retail",
        role="analyst",
        filters=QueryFilters(
            date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
        ),
    )
    response = execute_query(request, use_llm_polish=False)
    assert len(response.drivers) >= 1
