"""Golden question evaluation runner."""

from datetime import date

import logfire

from app.core.config import get_settings
from app.eval.golden_loader import load_golden_dataset
from app.models.eval_models import GoldenEvalReport
from app.models.query_models import DateRange, QueryFilters, QueryRequest
from app.services.query_pipeline import execute_query
from app.tools.eval_tools import build_report, evaluate_case


def _build_request(case: dict) -> QueryRequest:
    filters = None
    raw_filters = case.get("filters") or {}
    if raw_filters:
        dr = raw_filters.get("date_range")
        date_range = None
        if dr:
            date_range = DateRange(
                start_date=date.fromisoformat(dr["start_date"]),
                end_date=date.fromisoformat(dr["end_date"]),
            )
        filters = QueryFilters(
            date_range=date_range,
            store_id=raw_filters.get("store_id"),
            category=raw_filters.get("category"),
            sku=raw_filters.get("sku"),
        )

    role = case.get("role", "manager")
    mode = case.get("mode", role)
    if mode == "admin":
        mode = "analyst"

    return QueryRequest(
        question=case["question"],
        client_id=case.get("client_id", "demo-retail"),
        role=role,
        mode=mode,  # type: ignore[arg-type]
        detail_level=case.get("detail_level", "summary"),
        filters=filters,
        routing_hint=case.get("routing_hint"),
    )


def run_golden_eval(client_id: str, subset: str | None = None) -> GoldenEvalReport:
    settings = get_settings()
    cases = load_golden_dataset(client_id=client_id, subset=subset)

    with logfire.span("golden_eval", client_id=client_id, subset=subset, cases=len(cases)):
        results = []
        for case in cases:
            request = _build_request(case)
            response = execute_query(request, use_llm_polish=False)
            results.append(evaluate_case(case, response))

    return build_report(client_id, results, settings)
