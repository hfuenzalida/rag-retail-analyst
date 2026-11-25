"""Evaluation tools for faithfulness, relevance, and golden-question runs."""

from decimal import Decimal

from app.models.eval_models import EvalScore, GoldenCaseResult, GoldenEvalReport
from app.models.query_models import QueryRequest, QueryResponse


def evaluate_answer_faithfulness(answer: QueryResponse, expected: dict) -> EvalScore:
    """Check numeric and structural correctness against expected values."""
    if expected.get("requires_abstention"):
        passed = answer.error is not None and answer.error.code in {
            expected.get("abstention_code", "ABSTAIN"),
            "ABSTAIN",
            "PERMISSION_DENIED",
        }
        return EvalScore(
            name="factual_accuracy",
            passed=passed,
            score=1.0 if passed else 0.0,
            details="Abstention expected" if passed else f"Expected abstention, got {answer.error}",
        )

    metric_name = expected.get("metric_name")
    if not metric_name:
        if expected.get("requires_drivers"):
            passed = len(answer.drivers) > 0
            return EvalScore(
                name="factual_accuracy",
                passed=passed,
                score=1.0 if passed else 0.0,
                details="Expected drivers" if passed else "No drivers returned",
            )
        return EvalScore(name="factual_accuracy", passed=True, score=1.0, details="No metric expectation")

    matching = [m for m in answer.metrics if m.name == metric_name]
    if not matching:
        return EvalScore(
            name="factual_accuracy",
            passed=False,
            score=0.0,
            details=f"Missing metric {metric_name}",
        )

    expected_value = Decimal(str(expected["value"]))
    tolerance = Decimal(str(expected.get("tolerance_pct", 0.01)))
    actual = Decimal(str(matching[0].value))
    if expected_value == 0:
        passed = actual == 0
    else:
        delta = abs(actual - expected_value) / abs(expected_value)
        passed = delta <= tolerance

    return EvalScore(
        name="factual_accuracy",
        passed=passed,
        score=1.0 if passed else 0.0,
        details=f"{metric_name}: expected {expected_value}, got {actual}",
    )


def evaluate_answer_groundedness(answer: QueryResponse, expected: dict) -> EvalScore:
    if expected.get("requires_abstention"):
        return EvalScore(name="groundedness", passed=True, score=1.0, details="Abstention case")

    if not answer.metrics and not answer.drivers:
        passed = answer.error is not None
        return EvalScore(
            name="groundedness",
            passed=passed,
            score=1.0 if passed else 0.0,
            details="Missing data handled with error" if passed else "Empty answer without error",
        )

    data_citations = [c for c in answer.citations if c.type == "data"]
    passed = len(data_citations) >= 1 or len(answer.metrics) == 0
    return EvalScore(
        name="groundedness",
        passed=passed,
        score=1.0 if passed else 0.0,
        details=f"{len(data_citations)} data citations",
    )


def evaluate_abstention_behavior(answer: QueryResponse, expected: dict) -> EvalScore:
    if not expected.get("requires_abstention"):
        hallucinated = answer.metrics and answer.error and answer.error.code == "ABSTAIN"
        passed = not hallucinated
        return EvalScore(
            name="abstention_correct",
            passed=passed,
            score=1.0 if passed else 0.0,
            details="Non-abstention case",
        )

    passed = answer.error is not None and answer.error.code in {"ABSTAIN", "PERMISSION_DENIED"}
    return EvalScore(
        name="abstention_correct",
        passed=passed,
        score=1.0 if passed else 0.0,
        details=f"error={answer.error.code if answer.error else None}",
    )


def evaluate_format_validity(answer: QueryResponse, expected: dict) -> EvalScore:
    routing_ok = answer.routing_decision in {"local_only", "cloud_assist", "cloud_only"}
    summary_ok = bool(answer.summary.strip())
    expected_routing = expected.get("routing_decision")
    if expected_routing:
        routing_ok = answer.routing_decision == expected_routing
    passed = routing_ok and summary_ok
    return EvalScore(
        name="format_valid",
        passed=passed,
        score=1.0 if passed else 0.0,
        details=f"routing={answer.routing_decision}, summary_len={len(answer.summary)}",
    )


def evaluate_case(case: dict, answer: QueryResponse) -> GoldenCaseResult:
    expected = case.get("expected", {})
    factual = evaluate_answer_faithfulness(answer, expected)
    grounded = evaluate_answer_groundedness(answer, expected)
    abstention = evaluate_abstention_behavior(answer, expected)
    format_valid = evaluate_format_validity(answer, expected)
    passed = all(s.passed for s in [factual, grounded, abstention, format_valid])
    failures = [s.details for s in [factual, grounded, abstention, format_valid] if not s.passed]
    return GoldenCaseResult(
        case_id=case["id"],
        question=case["question"],
        passed=passed,
        factual_accuracy=factual,
        groundedness=grounded,
        abstention_correct=abstention,
        format_valid=format_valid,
        failure_modes=failures,
    )


def build_report(client_id: str, case_results: list[GoldenCaseResult], settings) -> GoldenEvalReport:
    total = len(case_results)
    if total == 0:
        return GoldenEvalReport(
            client_id=client_id,
            total_cases=0,
            passed_cases=0,
            factual_accuracy_rate=0.0,
            groundedness_rate=0.0,
            abstention_correct_rate=0.0,
            format_valid_rate=0.0,
            meets_thresholds=False,
        )

    passed_cases = sum(1 for c in case_results if c.passed)
    factual_rate = sum(c.factual_accuracy.score for c in case_results) / total
    grounded_rate = sum(c.groundedness.score for c in case_results) / total
    abstention_rate = sum(c.abstention_correct.score for c in case_results) / total
    format_rate = sum(c.format_valid.score for c in case_results) / total

    meets = (
        factual_rate >= settings.eval_min_factual_accuracy
        and grounded_rate >= settings.eval_min_groundedness
        and abstention_rate >= 1.0
        and format_rate >= 1.0
    )

    return GoldenEvalReport(
        client_id=client_id,
        total_cases=total,
        passed_cases=passed_cases,
        factual_accuracy_rate=round(factual_rate, 4),
        groundedness_rate=round(grounded_rate, 4),
        abstention_correct_rate=round(abstention_rate, 4),
        format_valid_rate=round(format_rate, 4),
        meets_thresholds=meets,
        cases=case_results,
    )
