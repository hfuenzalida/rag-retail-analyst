"""Ingestion / schema mapping agent (propose-only in v1)."""

from app.models.ingest import MappingSuggestion, TableName
from app.services.ingestion import propose_csv_mapping


def map_csv_to_schema(
    client_id: str,
    table_name: TableName,
    headers: list[str],
    sample_rows: list[list[str]],
) -> MappingSuggestion:
    """
    Propose CSV column mappings to canonical schema fields.
    Does not persist or load data — admin must confirm via /ingest/csv/confirm.
    """
    return propose_csv_mapping(
        client_id=client_id,
        table_name=table_name,
        headers=headers,
        sample_rows=sample_rows,
    )
