"""Evaluation tool unit tests."""

from decimal import Decimal

from app.models.query_models import Citation, ErrorInfo, Metric, QueryResponse
from app.tools.eval_tools import (
    build_report,
    evaluate_abstention_behavior,
    evaluate_answer_faithfulness,
    evaluate_answer_groundedness,
    evaluate_case,
    evaluate_format_validity,
)


def _answer(**kwargs) -> QueryResponse:
    defaults = {
        "summary": "Revenue was 1640.",
        "metrics": [],
        "drivers": [],
        "recommendations": [],
        "citations": [],
        "routing_decision": "local_only",
        "error": None,
    }
    defaults.update(kwargs)
    return QueryResponse(**defaults)


def test_faithfulness_passes_matching_metric():
    answer = _answer(metrics=[Metric(name="total_revenue", value=Decimal("1640"), unit="currency")])
    score = evaluate_answer_faithfulness(answer, {"metric_name": "total_revenue", "value": 1640})
    assert score.passed


def test_faithfulness_abstention_case():
    answer = _answer(error=ErrorInfo(code="ABSTAIN", message="Cannot answer"), summary="")
    score = evaluate_answer_faithfulness(answer, {"requires_abstention": True})
    assert score.passed


def test_groundedness_requires_data_citation():
    answer = _answer(
        metrics=[Metric(name="total_revenue", value=Decimal("100"), unit="currency")],
        citations=[],
    )
    score = evaluate_answer_groundedness(answer, {})
    assert not score.passed


def test_evaluate_case_builds_report():
    case = {
        "id": "case-1",
        "question": "Revenue?",
        "expected": {"metric_name": "total_revenue", "value": 1640},
    }
    answer = _answer(
        metrics=[Metric(name="total_revenue", value=Decimal("1640"), unit="currency")],
        citations=[Citation(type="data", source="sales", reference="sales_table")],
    )
    result = evaluate_case(case, answer)
    assert result.case_id == "case-1"

    class Settings:
        eval_min_factual_accuracy = 0.95
        eval_min_groundedness = 0.98

    report = build_report("demo-retail", [result], Settings())
    assert report.total_cases == 1
    assert report.meets_thresholds
