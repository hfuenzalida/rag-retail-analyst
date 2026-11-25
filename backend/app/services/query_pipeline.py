"""End-to-end query orchestration: routing → tools → grounded response."""

from decimal import Decimal

import logfire

from app.core.config import get_settings
from app.core.fallbacks import polish_with_fallback
from app.core.rollout import is_feature_available_for_role
from app.core.runtime_controls import is_feature_enabled, is_kill_switch_active
from app.models.metrics import MetricResult
from app.models.query_models import (
    Action,
    Citation,
    Driver,
    ErrorInfo,
    Metric,
    QueryRequest,
    QueryResponse,
)
from app.models.routing import RoutingDecisionResult
from app.services.intent import classify_intent, driver_window, effective_filters
from app.tools.metrics_tools import get_top_drivers, run_metric_query
from app.tools.rag_tools import get_schema_docs, search_docs
from app.tools.rbac import PermissionDeniedError
from app.models.rag import DocFilters
from app.tools.routing_tools import check_sensitivity, log_routing_decision, resolve_routing_decision


def _metric_to_model(result: MetricResult) -> Metric:
    return Metric(
        name=result.name,
        value=result.value,
        unit=result.unit,
        time_window=result.time_window,
        context=result.context,
    )


def _build_recommendations(
    metrics: list[Metric], drivers: list[Driver], role: str
) -> list[Action]:
    if not is_feature_available_for_role("recommendation_engine", role):  # type: ignore[arg-type]
        return []
    if is_kill_switch_active("automated_recommendations") or not is_feature_enabled(
        "recommendation_engine", default=True
    ):
        return []

    actions: list[Action] = []
    for metric in metrics:
        if metric.name == "stock_out_rate" and metric.value >= Decimal("20"):
            actions.append(
                Action(
                    label="Review reorder points",
                    description=(
                        f"Stock-out rate is {metric.value}%. Review reorder points and safety stock for affected SKUs."
                    ),
                    priority="high",
                    type="inventory",
                )
            )
    for driver in drivers[:2]:
        if driver.impact < 0:
            actions.append(
                Action(
                    label=f"Investigate {driver.dimension}",
                    description=f"Negative driver: {driver.description}",
                    priority="medium",
                    type="other",
                )
            )
    return actions


def _build_summary(
    request: QueryRequest,
    metrics: list[Metric],
    drivers: list[Driver],
    abstain_reason: str | None,
) -> str:
    if abstain_reason:
        return abstain_reason

    if not metrics and not drivers:
        return "I don't have enough data to answer this confidently."

    parts: list[str] = []
    for metric in metrics:
        window = ""
        if metric.time_window:
            window = f" ({metric.time_window.start_date} to {metric.time_window.end_date})"
        unit = f" {metric.unit}" if metric.unit else ""
        parts.append(f"{metric.name.replace('_', ' ')}: {metric.value}{unit}{window}.")

    if drivers:
        top = drivers[0]
        parts.append(f"Largest driver: {top.description}")

    summary = " ".join(parts)
    effective_detail = request.detail_level
    if request.detail_level == "deep_dive" and not is_feature_available_for_role(
        "deep_dive_mode", request.role
    ):
        effective_detail = "summary"
    if effective_detail == "deep_dive" and drivers:
        extra = "; ".join(d.description for d in drivers[1:3])
        if extra:
            summary += f" Additional drivers: {extra}."
    return summary


def execute_query(request: QueryRequest, *, use_llm_polish: bool = True) -> QueryResponse:
    """Run the bounded analyst pipeline with grounded tool outputs."""
    with logfire.span("query_pipeline", client_id=request.client_id, question=request.question):
        sensitivity = check_sensitivity(request.question)
        routing = log_routing_decision(resolve_routing_decision(request, sensitivity))
        intent = classify_intent(request)
        filters = effective_filters(request)

        if intent.abstain_reason:
            return QueryResponse(
                summary=intent.abstain_reason,
                confidence=0.0,
                routing_decision=routing.routing_decision,
                error=ErrorInfo(
                    code="ABSTAIN",
                    message=intent.abstain_reason,
                    retry_hint="Rephrase the question or adjust filters.",
                ),
            )

        metrics: list[Metric] = []
        drivers: list[Driver] = []
        citations: list[Citation] = []
        errors: list[str] = []

        for metric_name in intent.metrics:
            try:
                with logfire.span("tool.run_metric_query", metric=metric_name):
                    result = run_metric_query(metric_name, request.client_id, request.role, filters)
                    metrics.append(_metric_to_model(result))
                    citations.append(
                        Citation(type="data", source="sales/inventory", reference=f"metric:{metric_name}")
                    )
            except PermissionDeniedError as exc:
                return QueryResponse(
                    summary=str(exc),
                    routing_decision=routing.routing_decision,
                    confidence=0.0,
                    error=ErrorInfo(code="PERMISSION_DENIED", message=str(exc)),
                )
            except ValueError as exc:
                errors.append(str(exc))

        if intent.driver_metric and intent.driver_dimension:
            if not is_feature_available_for_role("driver_analysis", request.role):
                errors.append("Driver analysis is not enabled for your role in the current rollout.")
            else:
                try:
                    with logfire.span("tool.get_top_drivers", dimension=intent.driver_dimension):
                        driver_results = get_top_drivers(
                            intent.driver_metric,
                            intent.driver_dimension,
                            driver_window(request),
                            request.client_id,
                            request.role,
                            filters,
                        )
                        drivers = [d.to_driver() for d in driver_results]
                        for d in driver_results[:3]:
                            citations.append(
                                Citation(
                                    type="data",
                                    source="sales",
                                    reference=f"driver:{d.dimension}:{d.dimension_value}",
                                )
                            )
                except (PermissionDeniedError, ValueError) as exc:
                    errors.append(str(exc))

        if intent.schema_lookup:
            with logfire.span("tool.get_schema_docs", target=intent.schema_lookup):
                docs = get_schema_docs(intent.schema_lookup, request.client_id, k=2)
                for doc in docs:
                    citations.append(
                        Citation(type="document", source=doc.source, reference=f"doc:{doc.id}")
                    )

        if intent.doc_search:
            with logfire.span("tool.search_docs"):
                doc_filters = DocFilters(client_id=request.client_id)
                docs = search_docs(intent.doc_search, k=2, filters=doc_filters)
                for doc in docs:
                    citations.append(
                        Citation(type="document", source=doc.source, reference=f"doc:{doc.id}")
                    )

        if not metrics and not drivers and errors:
            return QueryResponse(
                summary="I don't have enough data to answer this confidently.",
                routing_decision=routing.routing_decision,
                confidence=0.0,
                error=ErrorInfo(
                    code="DATA_MISSING",
                    message=errors[0],
                    retry_hint="Verify data ingestion or narrow filters.",
                ),
            )

        recommendations = _build_recommendations(metrics, drivers, request.role)
        summary = _build_summary(request, metrics, drivers, None)

        if use_llm_polish:
            settings = get_settings()
            summary, _fallback = polish_with_fallback(request.question, summary, routing, settings)

        confidence = 0.9 if metrics else 0.6
        if drivers:
            confidence = min(0.95, confidence + 0.05)

        return QueryResponse(
            summary=summary,
            metrics=metrics,
            drivers=drivers,
            recommendations=recommendations,
            citations=citations,
            confidence=confidence,
            routing_decision=routing.routing_decision,
        )
