"""Production tenant boundary API tests."""

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_query_rejects_unauthorized_client_in_production(monkeypatch):
    monkeypatch.setenv("APP_APP_ENV", "production")
    monkeypatch.setenv("APP_PILOT_CLIENT_ID", "demo-retail")
    from app.core.config import get_settings

    get_settings.cache_clear()

    response = client.post(
        "/query",
        json={"question": "What was revenue?", "client_id": "wrong-client", "role": "manager"},
    )
    assert response.status_code == 403
    get_settings.cache_clear()


def test_query_allows_pilot_client_in_production(monkeypatch):
    monkeypatch.setenv("APP_APP_ENV", "production")
    monkeypatch.setenv("APP_PILOT_CLIENT_ID", "demo-retail")
    from app.core.config import get_settings

    get_settings.cache_clear()

    with patch("app.services.query_pipeline.search_docs", return_value=[]), patch(
        "app.services.query_pipeline.get_schema_docs", return_value=[]
    ), patch("app.services.query_pipeline.run_metric_query") as mock_metric:
        from decimal import Decimal

        from app.models.metrics import MetricResult

        mock_metric.return_value = MetricResult(name="total_revenue", value=Decimal("100"), unit="currency")
        response = client.post(
            "/query",
            json={"question": "What was revenue?", "client_id": "demo-retail", "role": "manager"},
        )
    assert response.status_code == 200
    get_settings.cache_clear()
