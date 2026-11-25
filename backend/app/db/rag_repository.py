"""PostgreSQL storage and hybrid retrieval for RAG documents."""

from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb

from app.models.rag import DocChunk, DocFilters
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_text


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"


def insert_document(
    conn: Connection,
    client_id: str,
    content: str,
    metadata: dict[str, Any],
) -> int:
    embedding = embed_text(content)
    row = conn.execute(
        """
        INSERT INTO rag_documents (client_id, content, metadata, embedding)
        VALUES (%s, %s, %s, %s::vector)
        RETURNING id
        """,
        [client_id, content, Jsonb(metadata), _vector_literal(embedding)],
    ).fetchone()
    return int(row["id"])


def ingest_text_document(
    conn: Connection,
    client_id: str,
    content: str,
    metadata: dict[str, Any],
) -> tuple[int, list[int]]:
    chunks = chunk_text(content)
    if not chunks:
        return 0, []

    ids: list[int] = []
    for chunk in chunks:
        chunk_meta = {
            **metadata,
            "chunk_index": chunk.index,
            "chunk_total": len(chunks),
        }
        doc_id = insert_document(conn, client_id, chunk.content, chunk_meta)
        ids.append(doc_id)
    return len(ids), ids


def _filter_clause(filters: DocFilters) -> tuple[str, list[Any]]:
    clauses = ["client_id = %s"]
    params: list[Any] = [filters.client_id]

    if filters.doc_type:
        clauses.append("metadata->>'doc_type' = %s")
        params.append(filters.doc_type)

    if filters.date_range:
        start, end = filters.date_range
        clauses.append("(metadata->>'doc_date')::date BETWEEN %s AND %s")
        params.extend([start, end])

    return " AND ".join(clauses), params


def search_documents(
    conn: Connection,
    text_query: str,
    k: int,
    filters: DocFilters,
) -> list[DocChunk]:
    where, params = _filter_clause(filters)
    query_embedding = embed_text(text_query)
    vector_param = _vector_literal(query_embedding)

    sql = f"""
        SELECT
            id,
            content,
            metadata,
            (
                0.6 * (1 - (embedding <=> %s::vector))
                + 0.4 * ts_rank(
                    to_tsvector('english', content),
                    plainto_tsquery('english', %s)
                )
            ) AS score
        FROM rag_documents
        WHERE {where}
          AND (
            to_tsvector('english', content) @@ plainto_tsquery('english', %s)
            OR embedding IS NOT NULL
          )
        ORDER BY score DESC
        LIMIT %s
    """
    bind = [vector_param, text_query, *params, text_query, k]
    rows = conn.execute(sql, bind).fetchall()

    results: list[DocChunk] = []
    for row in rows:
        metadata = row["metadata"] or {}
        source = metadata.get("title") or metadata.get("doc_type") or "rag_documents"
        results.append(
            DocChunk(
                id=int(row["id"]),
                content=row["content"],
                score=float(row["score"] or 0),
                metadata=metadata,
                source=str(source),
            )
        )
    return results


def search_schema_documents(
    conn: Connection,
    table_or_metric_name: str,
    client_id: str,
    k: int = 5,
) -> list[DocChunk]:
    filters = DocFilters(client_id=client_id, doc_type="schema")
    query = f"{table_or_metric_name} schema metric definition"
    return search_documents(conn, query, k, filters)
