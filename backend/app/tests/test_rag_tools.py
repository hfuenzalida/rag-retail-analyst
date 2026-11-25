"""RAG tool tests with mocked database."""

from unittest.mock import patch

from app.models.rag import DocChunk, DocFilters
from app.tools.rag_tools import get_schema_docs, search_docs


@patch("app.tools.rag_tools.search_documents")
@patch("app.tools.rag_tools.get_connection")
def test_search_docs(mock_conn, mock_search):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None
    mock_search.return_value = [
        DocChunk(id=1, content="inventory schema", score=0.9, metadata={"doc_type": "schema"}, source="schema")
    ]
    filters = DocFilters(client_id="demo-retail")
    results = search_docs("inventory stock", k=3, filters=filters)
    assert len(results) == 1
    mock_search.assert_called_once()


@patch("app.tools.rag_tools.search_schema_documents")
@patch("app.tools.rag_tools.get_connection")
def test_get_schema_docs(mock_conn, mock_schema):
    mock_conn.return_value.__enter__.return_value = object()
    mock_conn.return_value.__exit__.return_value = None
    mock_schema.return_value = [
        DocChunk(id=2, content="total_revenue metric", score=0.95, metadata={}, source="metric")
    ]
    results = get_schema_docs("total_revenue", "demo-retail")
    assert results[0].content.startswith("total_revenue")


def test_search_docs_rejects_invalid_k():
    try:
        search_docs("test", k=0, filters=DocFilters(client_id="demo-retail"))
        assert False, "expected ValueError"
    except ValueError:
        pass
