"""RAG retrieval tools for agents."""

from app.db.connection import get_connection
from app.db.rag_repository import search_documents, search_schema_documents
from app.models.rag import DocChunk, DocFilters


def search_docs(text_query: str, k: int, filters: DocFilters) -> list[DocChunk]:
    """Hybrid vector + keyword search over the local RAG index."""
    if k <= 0:
        raise ValueError("k must be positive")
    with get_connection() as conn:
        return search_documents(conn, text_query=text_query, k=k, filters=filters)


def get_schema_docs(table_or_metric_name: str, client_id: str, k: int = 5) -> list[DocChunk]:
    """Retrieve schema and metric documentation chunks."""
    with get_connection() as conn:
        return search_schema_documents(
            conn,
            table_or_metric_name=table_or_metric_name,
            client_id=client_id,
            k=k,
        )
