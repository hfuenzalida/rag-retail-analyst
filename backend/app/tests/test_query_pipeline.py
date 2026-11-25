"""Query pipeline and golden smoke tests."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.metrics import DriverResult, MetricResult
from app.models.query_models import DateRange, QueryFilters, QueryRequest
from app.models.rag import DocChunk
from app.services.query_pipeline import execute_query

SMOKE_CASES = [
    {
        "id": "smoke-001",
        "request": QueryRequest(
            question="What was total net revenue last month?",
            client_id="demo-retail",
            role="manager",
            filters=QueryFilters(
                date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
            ),
        ),
        "expect_metric": "total_revenue",
    },
    {
        "id": "smoke-002",
        "request": QueryRequest(
            question="Which SKUs are currently out of stock?",
            client_id="demo-retail",
            role="manager",
        ),
        "expect_metric": "stock_out_rate",
    },
    {
        "id": "smoke-003",
        "request": QueryRequest(
            question="How many units did we sell?",
            client_id="demo-retail",
            role="manager",
        ),
        "expect_metric": "units_sold",
    },
    {
        "id": "smoke-004",
        "request": QueryRequest(
            question="Why did revenue change by category?",
            client_id="demo-retail",
            role="analyst",
            filters=QueryFilters(
                date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
            ),
        ),
        "expect_drivers": True,
    },
    {
        "id": "smoke-005",
        "request": QueryRequest(
            question="What is gross margin percent?",
            client_id="demo-retail",
            role="analyst",
        ),
        "expect_metric": "gross_margin_pct",
    },
    {
        "id": "smoke-006",
        "request": QueryRequest(
            question="What is gross margin percent?",
            client_id="demo-retail",
            role="manager",
        ),
        "expect_error": "ABSTAIN",
    },
    {
        "id": "smoke-007",
        "request": QueryRequest(
            question="Show customer salary details",
            client_id="demo-retail",
            role="analyst",
        ),
        "expect_error": "ABSTAIN",
    },
    {
        "id": "smoke-008",
        "request": QueryRequest(
            question="What was revenue last month?",
            client_id="demo-retail",
            role="manager",
            routing_hint="local_only",
        ),
        "expect_routing": "local_only",
    },
    {
        "id": "smoke-009",
        "request": QueryRequest(
            question="Explain stock out risk",
            client_id="demo-retail",
            role="manager",
        ),
        "expect_metric": "stock_out_rate",
    },
    {
        "id": "smoke-010",
        "request": QueryRequest(
            question="Revenue variance by store",
            client_id="demo-retail",
            role="analyst",
            filters=QueryFilters(
                date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
            ),
        ),
        "expect_drivers": True,
    },
]


@patch("app.services.query_pipeline.search_docs", return_value=[])
@patch("app.services.query_pipeline.get_schema_docs", return_value=[])
@patch("app.services.query_pipeline.get_top_drivers")
@patch("app.services.query_pipeline.run_metric_query")
def test_golden_smoke_cases(mock_metric, mock_drivers, mock_schema, mock_search):
    mock_metric.return_value = MetricResult(
        name="total_revenue", value=Decimal("1640"), unit="currency"
    )
    mock_drivers.return_value = [
        DriverResult(
            dimension="category",
            dimension_value="Shoes",
            impact=Decimal("-1260"),
            current_value=Decimal("940"),
            prior_value=Decimal("2200"),
            description="Shoes decreased",
        )
    ]

    def metric_side_effect(name, client_id, role, filters=None):
        return MetricResult(name=name, value=Decimal("1640") if name == "total_revenue" else Decimal("33.33"), unit="x")

    mock_metric.side_effect = metric_side_effect

    for case in SMOKE_CASES:
        response = execute_query(case["request"], use_llm_polish=False)
        if case.get("expect_error"):
            assert response.error is not None
            assert response.error.code == case["expect_error"], case["id"]
            continue
        if case.get("expect_metric"):
            assert any(m.name == case["expect_metric"] for m in response.metrics), case["id"]
        if case.get("expect_drivers"):
            assert len(response.drivers) >= 1, case["id"]
        if case.get("expect_routing"):
            assert response.routing_decision == case["expect_routing"], case["id"]
        assert response.summary
        assert response.routing_decision == "local_only"


@patch("app.services.query_pipeline.search_docs", return_value=[])
@patch("app.services.query_pipeline.get_schema_docs", return_value=[])
@patch("app.services.query_pipeline.run_metric_query")
def test_pipeline_data_missing(mock_metric, mock_schema, mock_search):
    mock_metric.side_effect = ValueError("No inventory records found")
    response = execute_query(
        QueryRequest(question="Which SKUs are out of stock?", client_id="demo-retail"),
        use_llm_polish=False,
    )
    assert response.error is not None
    assert response.error.code == "DATA_MISSING"


@patch("app.services.query_pipeline.get_schema_docs")
@patch("app.services.query_pipeline.run_metric_query")
def test_pipeline_includes_citations(mock_metric, mock_schema):
    mock_metric.return_value = MetricResult(name="total_revenue", value=Decimal("100"), unit="currency")
    mock_schema.return_value = [
        DocChunk(id=1, content="metric docs", score=0.9, metadata={}, source="schema")
    ]
    response = execute_query(
        QueryRequest(question="What was revenue?", client_id="demo-retail"),
        use_llm_polish=False,
    )
    assert len(response.citations) >= 2
