"""API integration tests."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.metrics import MetricResult
from app.models.query_models import DateRange

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "rag-retail-analyst"
    assert "read_only" in data
    assert "ingest_enabled" in data


@patch("app.services.query_pipeline.search_docs", return_value=[])
@patch("app.services.query_pipeline.get_schema_docs", return_value=[])
@patch("app.services.query_pipeline.run_metric_query")
def test_query_returns_structured_response(mock_metric, mock_schema, mock_search):
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
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["metrics"]
    assert data["routing_decision"] == "local_only"
