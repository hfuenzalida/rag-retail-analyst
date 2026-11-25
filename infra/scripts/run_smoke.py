#!/usr/bin/env python3
"""Smoke tests for deployed or in-process API (health + canary questions)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

CANARY_QUESTIONS = [
    {
        "question": "What was total net revenue last month?",
        "client_id": "demo-retail",
        "role": "manager",
        "expect_routing": "local_only",
    },
    {
        "question": "Show customer salary details",
        "client_id": "demo-retail",
        "role": "analyst",
        "expect_error": "ABSTAIN",
    },
]


def run_inprocess_smoke() -> int:
    from datetime import date
    from decimal import Decimal
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from app.main import app
    from app.models.metrics import MetricResult
    from app.models.query_models import DateRange

    client = TestClient(app)

    health = client.get("/healthz")
    if health.status_code != 200:
        print(f"healthz failed: {health.status_code}", file=sys.stderr)
        return 1
    print(f"healthz ok env={health.json().get('app_env')}")

    with patch("app.services.query_pipeline.search_docs", return_value=[]), patch(
        "app.services.query_pipeline.get_schema_docs", return_value=[]
    ), patch("app.services.query_pipeline.run_metric_query") as mock_metric:
        mock_metric.return_value = MetricResult(
            name="total_revenue",
            value=Decimal("1640"),
            unit="currency",
            time_window=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31)),
        )

        for case in CANARY_QUESTIONS:
            response = client.post("/query", json=case)
            if response.status_code != 200:
                print(f"query failed for {case['question']}: {response.status_code}", file=sys.stderr)
                return 1
            data = response.json()
            if case.get("expect_routing") and data.get("routing_decision") != case["expect_routing"]:
                print(f"routing mismatch: {data.get('routing_decision')}", file=sys.stderr)
                return 1
            if case.get("expect_error"):
                err = data.get("error") or {}
                if err.get("code") != case["expect_error"]:
                    print(f"expected error {case['expect_error']}, got {err}", file=sys.stderr)
                    return 1
            print(f"canary ok: {case['question'][:40]}...")

    return 0


def run_remote_smoke(base_url: str) -> int:
    import httpx

    with httpx.Client(timeout=30.0) as client:
        health = client.get(f"{base_url.rstrip('/')}/healthz")
        if health.status_code != 200:
            print(f"healthz failed: {health.status_code}", file=sys.stderr)
            return 1
        print(f"healthz ok env={health.json().get('app_env')}")

        for case in CANARY_QUESTIONS:
            response = client.post(f"{base_url.rstrip('/')}/query", json=case)
            if response.status_code != 200:
                print(f"query failed: {response.status_code}", file=sys.stderr)
                return 1
            data = response.json()
            if case.get("expect_error"):
                err = data.get("error") or {}
                if err.get("code") != case["expect_error"]:
                    return 1
            print(f"canary ok: {case['question'][:40]}...")
    return 0


def main() -> int:
    base_url = os.environ.get("SMOKE_BASE_URL")
    if base_url:
        return run_remote_smoke(base_url)
    return run_inprocess_smoke()


if __name__ == "__main__":
    raise SystemExit(main())
