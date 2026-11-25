"""Controls API tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.controls_models import RuntimeControlsSnapshot, RuntimeDefaults

client = TestClient(app)
ADMIN_HEADERS = {"X-Role": "admin"}


@patch("app.api.controls.load_runtime_controls")
def test_get_runtime_controls_requires_admin(mock_load):
    mock_load.return_value = RuntimeControlsSnapshot(
        defaults=RuntimeDefaults(),
        feature_flags={"cloud_routing": False},
        kill_switches={"cloud_routing": False},
    )
    denied = client.get("/controls/runtime", headers={"X-Role": "manager"})
    assert denied.status_code == 403

    response = client.get("/controls/runtime", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert "feature_flags" in response.json()


@patch("app.api.controls.apply_runtime_controls_update")
def test_patch_runtime_controls(mock_apply):
    mock_apply.return_value = RuntimeControlsSnapshot(
        feature_flags={"cloud_routing": True},
        kill_switches={"cloud_routing": False},
    )
    response = client.patch(
        "/controls/runtime",
        headers=ADMIN_HEADERS,
        json={"feature_flags": {"cloud_routing": True}},
    )
    assert response.status_code == 200
    assert response.json()["feature_flags"]["cloud_routing"] is True


def test_ingest_allowed_probe():
    response = client.get("/controls/runtime/ingest-allowed")
    assert response.status_code == 200
    assert "ingest_allowed" in response.json()
