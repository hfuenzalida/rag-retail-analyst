"""CSV ingestion and schema mapping models."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

TableName = Literal["sales", "inventory", "products"]
MappingStatus = Literal["proposed", "confirmed"]


class FieldMapping(BaseModel):
    source_column: str
    target_field: str
    confidence: float
    required: bool = False


class MappingSuggestion(BaseModel):
    client_id: str
    table_name: TableName
    mappings: list[FieldMapping]
    unmapped_columns: list[str]
    missing_required_fields: list[str]
    warnings: list[str] = Field(default_factory=list)


class CsvMapRequest(BaseModel):
    client_id: str
    table_name: TableName
    headers: list[str]
    sample_rows: list[list[str]]
    role: Literal["manager", "analyst", "admin"] = "admin"


class CsvConfirmRequest(BaseModel):
    client_id: str
    table_name: TableName
    headers: list[str]
    rows: list[list[str]]
    mappings: list[FieldMapping]
    role: Literal["manager", "analyst", "admin"] = "admin"


class CsvIngestResponse(BaseModel):
    rows_inserted: int
    table_name: TableName
    mapping_status: MappingStatus
