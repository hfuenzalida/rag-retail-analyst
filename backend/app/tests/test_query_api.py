"""Query API integration tests."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.metrics import MetricResult
from app.models.query_models import DateRange, QueryFilters

client = TestClient(app)


@patch("app.services.query_pipeline.search_docs", return_value=[])
@patch("app.services.query_pipeline.get_schema_docs", return_value=[])
@patch("app.services.query_pipeline.run_metric_query")
def test_query_endpoint_returns_grounded_metric(mock_metric, mock_schema, mock_search):
    mock_metric.return_value = MetricResult(
        name="total_revenue",
        value=Decimal("1640"),
        unit="currency",
        time_window=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31)),
    )
    response = client.post(
        "/query",
        json={
            "question": "What was total revenue last month?",
            "client_id": "demo-retail",
            "role": "manager",
            "filters": {
                "date_range": {"start_date": "2026-05-01", "end_date": "2026-05-31"},
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["routing_decision"] == "local_only"
    assert data["metrics"][0]["value"] == "1640"
    assert "1640" in data["summary"]
    assert data["error"] is None


@patch("app.agents.rag_analyst.execute_query")
@patch("app.agents.rag_analyst.evaluate_routing")
def test_run_analyst_query_delegates(mock_routing, mock_execute):
    import asyncio

    from app.agents.rag_analyst import run_analyst_query
    from app.models.query_models import QueryRequest, QueryResponse

    mock_execute.return_value = QueryResponse(summary="ok", confidence=0.9)
    request = QueryRequest(question="revenue?", client_id="demo-retail")
    result = asyncio.run(run_analyst_query(request))
    assert result.summary == "ok"
    mock_routing.assert_called_once()
