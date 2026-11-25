"""RAG repository unit tests."""

from unittest.mock import MagicMock, patch

from app.db.rag_repository import ingest_text_document, search_documents
from app.models.rag import DocFilters


@patch("app.db.rag_repository.embed_text", return_value=[0.1] * 384)
def test_ingest_text_document(mock_embed):
    conn = MagicMock()
    conn.execute.return_value.fetchone.side_effect = [{"id": 1}, {"id": 2}]
    chunks, ids = ingest_text_document(
        conn,
        client_id="demo-retail",
        content="Short note",
        metadata={"doc_type": "note", "title": "note"},
    )
    assert chunks == 1
    assert ids == [1]
    mock_embed.assert_called()


@patch("app.db.rag_repository.embed_text", return_value=[0.2] * 384)
def test_search_documents(mock_embed):
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = [
        {
            "id": 10,
            "content": "Metric total_revenue equals sum of net_revenue",
            "metadata": {"doc_type": "schema", "title": "total_revenue metric"},
            "score": 0.88,
        }
    ]
    filters = DocFilters(client_id="demo-retail", doc_type="schema")
    results = search_documents(conn, "total_revenue", k=3, filters=filters)
    assert results[0].id == 10
    assert results[0].score == 0.88
    mock_embed.assert_called_once_with("total_revenue")
