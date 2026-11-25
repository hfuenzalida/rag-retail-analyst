"""Auth API and JWT tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.auth import create_access_token, decode_access_token
from app.models.eval_models import GoldenEvalReport
from app.main import app

client = TestClient(app)


def test_issue_dev_token():
    response = client.post(
        "/auth/token",
        json={"client_id": "demo-retail", "role": "admin", "user_id": "test-admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["role"] == "admin"


def test_jwt_admin_access_to_eval():
    token = create_access_token(client_id="demo-retail", role="admin", user_id="eval-admin")
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.api.eval.run_eval_suite") as mock_run:
        mock_run.return_value = GoldenEvalReport(
            client_id="demo-retail",
            total_cases=1,
            passed_cases=1,
            factual_accuracy_rate=1.0,
            groundedness_rate=1.0,
            abstention_correct_rate=1.0,
            format_valid_rate=1.0,
            meets_thresholds=True,
        )
        response = client.post("/eval/run", headers=headers, json={"client_id": "demo-retail"})
    assert response.status_code == 200


def test_jwt_manager_denied_eval():
    token = create_access_token(client_id="demo-retail", role="manager")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/eval/run", headers=headers, json={"client_id": "demo-retail"})
    assert response.status_code == 403


def test_decode_access_token_roundtrip():
    token = create_access_token(client_id="demo-retail", role="analyst", user_id="u1")
    ctx = decode_access_token(token)
    assert ctx.client_id == "demo-retail"
    assert ctx.role == "analyst"
    assert ctx.user_id == "u1"
