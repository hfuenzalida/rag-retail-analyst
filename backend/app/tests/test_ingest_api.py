"""Ingest API tests."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
ADMIN_HEADERS = {"X-Role": "admin"}


def test_csv_map_requires_admin():
    response = client.post(
        "/ingest/csv/map",
        headers={"X-Role": "manager"},
        json={
            "client_id": "demo-retail",
            "table_name": "sales",
            "headers": ["ItemCode"],
            "sample_rows": [],
            "role": "admin",
        },
    )
    assert response.status_code == 403


@patch("app.api.ingest.save_proposed_mapping")
@patch("app.api.ingest.get_connection")
def test_csv_map_proposes_mapping(mock_conn, mock_save):
    conn = MagicMock()
    mock_conn.return_value.__enter__.return_value = conn
    mock_conn.return_value.__exit__.return_value = None

    response = client.post(
        "/ingest/csv/map",
        headers=ADMIN_HEADERS,
        json={
            "client_id": "demo-retail",
            "table_name": "sales",
            "headers": ["ItemCode", "SoldDate", "Qty", "Net"],
            "sample_rows": [["SHOE-001", "2026-06-01", "5", "400"]],
            "role": "admin",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == "demo-retail"
    assert any(m["target_field"] == "sku" for m in data["mappings"])
    mock_save.assert_called_once()


@patch("app.api.ingest.ingest_text_document", return_value=(1, [99]))
@patch("app.api.ingest.get_connection")
def test_ingest_document(mock_conn, mock_ingest):
    conn = MagicMock()
    mock_conn.return_value.__enter__.return_value = conn
    mock_conn.return_value.__exit__.return_value = None

    response = client.post(
        "/ingest/documents",
        headers=ADMIN_HEADERS,
        json={
            "client_id": "demo-retail",
            "content": "Weekend promotions drive shoe sales.",
            "doc_type": "playbook",
            "title": "Promo playbook",
        },
    )
    assert response.status_code == 200
    assert response.json()["chunks_created"] == 1


@patch("app.api.ingest.load_csv_rows", return_value=2)
@patch("app.api.ingest.get_connection")
def test_csv_confirm_loads_rows(mock_conn, mock_load):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None

    response = client.post(
        "/ingest/csv/confirm",
        headers=ADMIN_HEADERS,
        json={
            "client_id": "demo-retail",
            "table_name": "products",
            "headers": ["ItemCode", "category", "price"],
            "rows": [["SHOE-003", "Shoes", "90"]],
            "mappings": [
                {"source_column": "ItemCode", "target_field": "sku", "confidence": 0.9, "required": True},
                {"source_column": "category", "target_field": "category", "confidence": 1.0, "required": False},
                {"source_column": "price", "target_field": "unit_price", "confidence": 0.9, "required": True},
            ],
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert response.json()["rows_inserted"] == 2
