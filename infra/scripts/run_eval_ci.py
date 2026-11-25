#!/usr/bin/env python3
"""Run CI golden eval subset and exit non-zero if thresholds fail."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.eval_runner import run_golden_eval  # noqa: E402


def main() -> int:
    report = run_golden_eval(client_id="demo-retail", subset="ci")
    print(
        f"Golden eval (ci): {report.passed_cases}/{report.total_cases} passed | "
        f"factual={report.factual_accuracy_rate:.2%} "
        f"grounded={report.groundedness_rate:.2%} "
        f"abstention={report.abstention_correct_rate:.2%} "
        f"format={report.format_valid_rate:.2%}"
    )
    if not report.meets_thresholds:
        print("Eval thresholds NOT met.", file=sys.stderr)
        return 1
    print("Eval thresholds met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
