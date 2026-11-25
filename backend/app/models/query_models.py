"""Shared Pydantic models for API requests and responses."""

from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start_date: date
    end_date: date


class QueryFilters(BaseModel):
    date_range: Optional[DateRange] = None
    store_id: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    detail_level: Literal["summary", "deep_dive"] = "summary"
    mode: Literal["manager", "analyst"] = "manager"
    filters: Optional[QueryFilters] = None
    routing_hint: Optional[Literal["local_only", "hybrid", "cloud_assist"]] = None
    client_id: str
    role: Literal["manager", "analyst", "admin"] = "manager"


class Metric(BaseModel):
    name: str
    value: Decimal
    unit: Optional[str] = None
    time_window: Optional[DateRange] = None
    context: Optional[str] = None


class Driver(BaseModel):
    dimension: str
    impact: Decimal
    description: str


class Action(BaseModel):
    label: str
    description: str
    priority: Literal["low", "medium", "high"] = "medium"
    type: Literal["inventory", "pricing", "promotion", "other"] = "other"


class Citation(BaseModel):
    type: Literal["data", "document"]
    source: str
    reference: str


class ErrorInfo(BaseModel):
    code: str
    message: str
    retry_hint: Optional[str] = None


class QueryResponse(BaseModel):
    summary: str
    metrics: list[Metric] = Field(default_factory=list)
    drivers: list[Driver] = Field(default_factory=list)
    recommendations: list[Action] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    routing_decision: Literal["local_only", "cloud_assist", "cloud_only"] = "local_only"
    error: Optional[ErrorInfo] = None


class HealthResponse(BaseModel):
    status: str
    app_env: str
    app_name: str
    read_only: bool = False
    ingest_enabled: bool = True
