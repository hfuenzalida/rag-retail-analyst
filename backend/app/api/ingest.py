"""Admin ingestion endpoints."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.agents.ingestion_agent import map_csv_to_schema
from app.core.auth import UserContext, require_admin_user
from app.core.runtime_controls import ingest_allowed
from app.db.connection import get_connection
from app.db.rag_repository import ingest_text_document
from app.models.ingest import (
    CsvConfirmRequest,
    CsvIngestResponse,
    CsvMapRequest,
    MappingSuggestion,
)
from app.models.metrics import Role
from app.models.rag import IngestDocumentRequest, IngestDocumentResponse
from app.services.ingestion import TABLE_FIELDS, load_csv_rows, parse_csv_text, save_proposed_mapping

router = APIRouter()


def _require_ingest_enabled() -> None:
    if not ingest_allowed():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ingestion is disabled in this environment.",
        )


def _validate_required_mappings(table_name: str, mappings: list) -> list[str]:
    schema = TABLE_FIELDS[table_name]  # type: ignore[index]
    mapped_targets = {m.target_field for m in mappings}
    return [
        field
        for field, spec in schema.items()
        if spec["required"] and field not in mapped_targets
    ]


@router.post("/csv/map", response_model=MappingSuggestion)
async def propose_csv_mapping(
    request: CsvMapRequest,
    _: UserContext = Depends(require_admin_user),
) -> MappingSuggestion:
    _require_ingest_enabled()
    if request.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    suggestion = map_csv_to_schema(
        client_id=request.client_id,
        table_name=request.table_name,
        headers=request.headers,
        sample_rows=request.sample_rows,
    )
    with get_connection() as conn:
        save_proposed_mapping(conn, suggestion)
        conn.commit()
    return suggestion


@router.post("/csv/confirm", response_model=CsvIngestResponse)
async def confirm_csv_ingest(
    request: CsvConfirmRequest,
    _: UserContext = Depends(require_admin_user),
) -> CsvIngestResponse:
    _require_ingest_enabled()
    if request.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    missing = _validate_required_mappings(request.table_name, request.mappings)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required fields: {missing}",
        )
    with get_connection() as conn:
        rows_inserted = load_csv_rows(conn, request)
    return CsvIngestResponse(
        rows_inserted=rows_inserted,
        table_name=request.table_name,
        mapping_status="confirmed",
    )


@router.post("/csv", response_model=MappingSuggestion)
async def ingest_csv_upload(
    client_id: str = Form(...),
    table_name: str = Form(...),
    file: UploadFile = File(...),
    _: UserContext = Depends(require_admin_user),
) -> MappingSuggestion:
    _require_ingest_enabled()
    """Upload CSV and return a proposed mapping for admin review (does not load rows)."""
    if table_name not in TABLE_FIELDS:
        raise HTTPException(status_code=400, detail="table_name must be sales, inventory, or products")
    raw = (await file.read()).decode("utf-8")
    headers, rows = parse_csv_text(raw)
    suggestion = map_csv_to_schema(
        client_id=client_id,
        table_name=table_name,  # type: ignore[arg-type]
        headers=headers,
        sample_rows=rows[:5],
    )
    with get_connection() as conn:
        save_proposed_mapping(conn, suggestion)
        conn.commit()
    return suggestion


@router.post("/documents", response_model=IngestDocumentResponse)
async def ingest_document(
    request: IngestDocumentRequest,
    _: UserContext = Depends(require_admin_user),
) -> IngestDocumentResponse:
    _require_ingest_enabled()
    metadata = {
        "doc_type": request.doc_type,
        "title": request.title or request.doc_type,
        "tags": request.tags,
    }
    with get_connection() as conn:
        chunks, ids = ingest_text_document(
            conn,
            client_id=request.client_id,
            content=request.content,
            metadata=metadata,
        )
        conn.commit()
    return IngestDocumentResponse(chunks_created=chunks, document_ids=ids)


@router.post("/db-config")
async def ingest_db_config(_: UserContext = Depends(require_admin_user)) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="DB config registration will be implemented in a later phase.",
    )
