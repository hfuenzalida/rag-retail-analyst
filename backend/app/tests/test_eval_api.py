"""Eval API tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.eval_models import GoldenEvalReport

client = TestClient(app)
ADMIN_HEADERS = {"X-Role": "admin"}


@patch("app.api.eval.run_eval_suite")
def test_eval_run_requires_admin(mock_run):
    response = client.post(
        "/eval/run",
        headers={"X-Role": "manager"},
        json={"client_id": "demo-retail"},
    )
    assert response.status_code == 403
    mock_run.assert_not_called()


@patch("app.api.eval.run_eval_suite")
def test_eval_run_returns_report(mock_run):
    mock_run.return_value = GoldenEvalReport(
        client_id="demo-retail",
        total_cases=5,
        passed_cases=5,
        factual_accuracy_rate=1.0,
        groundedness_rate=1.0,
        abstention_correct_rate=1.0,
        format_valid_rate=1.0,
        meets_thresholds=True,
    )
    response = client.post(
        "/eval/run",
        headers=ADMIN_HEADERS,
        json={"client_id": "demo-retail", "subset": "ci"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meets_thresholds"] is True
    mock_run.assert_called_once_with(client_id="demo-retail", subset="ci")
