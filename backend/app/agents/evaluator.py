"""Evaluator agent — quality scoring and golden eval orchestration."""

from app.models.eval_models import GoldenEvalReport
from app.services.eval_runner import run_golden_eval
from app.tools.eval_tools import (
    evaluate_abstention_behavior,
    evaluate_answer_faithfulness,
    evaluate_answer_groundedness,
    evaluate_format_validity,
)


def run_eval_suite(client_id: str, subset: str | None = None) -> GoldenEvalReport:
    """Run golden-question evaluation suite for regression detection."""
    return run_golden_eval(client_id=client_id, subset=subset)


__all__ = [
    "run_eval_suite",
    "evaluate_answer_faithfulness",
    "evaluate_answer_groundedness",
    "evaluate_abstention_behavior",
    "evaluate_format_validity",
]
