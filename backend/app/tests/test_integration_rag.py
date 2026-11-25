"""Integration tests for RAG layer (optional — requires PostgreSQL)."""

import os

import pytest

from app.core.config import Settings
from app.db.connection import close_pool, get_connection, init_pool
from app.db.rag_repository import search_documents
from app.db.seed.demo_retail import seed_demo_retail
from app.models.rag import DocFilters
from app.tools.rag_tools import get_schema_docs, search_docs

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Set RUN_DB_INTEGRATION=1 with PostgreSQL running to execute",
)


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    settings = Settings(
        db_url=__import__("pydantic").SecretStr(
            os.getenv("APP_DB_URL", "postgresql://postgres:postgres@localhost:5432/rag_analyst")
        )
    )
    close_pool()
    init_pool(settings)
    with get_connection(settings) as conn:
        seed_demo_retail(conn)
    yield
    close_pool()


def test_schema_docs_retrieval(seeded_db):
    results = get_schema_docs("total_revenue", "demo-retail")
    assert len(results) >= 1
    assert "net_revenue" in results[0].content.lower()


def test_search_docs_playbook(seeded_db):
    settings = Settings(
        db_url=__import__("pydantic").SecretStr(
            os.getenv("APP_DB_URL", "postgresql://postgres:postgres@localhost:5432/rag_analyst")
        )
    )
    with get_connection(settings) as conn:
        from app.db.rag_repository import ingest_text_document

        ingest_text_document(
            conn,
            client_id="demo-retail",
            content="Run weekend promotions on shoes to lift revenue.",
            metadata={"doc_type": "playbook", "title": "Weekend promos"},
        )
        conn.commit()

    filters = DocFilters(client_id="demo-retail", doc_type="playbook")
    results = search_docs("weekend shoe promotions", k=2, filters=filters)
    assert any("weekend" in r.content.lower() for r in results)
