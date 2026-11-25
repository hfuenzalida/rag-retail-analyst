"""Load and expand golden evaluation dataset."""

import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parents[3] / "memory-bank" / "eval" / "golden-questions.json"


def _may_filters() -> dict:
    return {"date_range": {"start_date": "2026-05-01", "end_date": "2026-05-31"}}


def _generated_cases() -> list[dict]:
    """Programmatic cases to reach 50+ coverage without hand-maintaining every row."""
    cases: list[dict] = []
    revenue_questions = [
        "What was total net revenue last month?",
        "How much revenue did we make in May 2026?",
        "Total sales revenue for May?",
        "What was our net revenue in the selected period?",
        "Report total revenue for May.",
        "May revenue total?",
        "How much did we sell in May 2026?",
        "Net revenue May 2026?",
        "What is total revenue for the date range?",
        "Summarize May revenue.",
        "Revenue performance in May?",
        "What were May sales in dollars?",
        "Total revenue last month for demo retail?",
        "How much net revenue in May?",
        "Give me May total revenue.",
    ]
    for i, q in enumerate(revenue_questions, start=4):
        cases.append(
            {
                "id": f"retail-rev-{i:03d}",
                "client_id": "demo-retail",
                "role": "manager",
                "question": q,
                "filters": _may_filters(),
                "ci_smoke": i <= 6,
                "expected": {"metric_name": "total_revenue", "value": 1640, "tolerance_pct": 0.01},
            }
        )

    units_questions = [
        "How many units were sold in May?",
        "Total units sold last month?",
        "Units sold in May 2026?",
        "Quantity sold in the period?",
        "How many items did we sell in May?",
        "Unit volume for May?",
        "Total quantity in May sales?",
        "Units sold May 2026?",
        "Item count sold in May?",
        "May units sold total?",
    ]
    for i, q in enumerate(units_questions, start=1):
        cases.append(
            {
                "id": f"retail-units-{i:03d}",
                "client_id": "demo-retail",
                "role": "manager",
                "question": q,
                "filters": _may_filters(),
                "ci_smoke": i == 1,
                "expected": {"metric_name": "units_sold", "value": 31, "tolerance_pct": 0.01},
            }
        )

    stock_questions = [
        "Which SKUs are out of stock?",
        "What is our stock-out rate?",
        "How many products are out of stock?",
        "Inventory stock out percentage?",
        "Current stock-out risk snapshot?",
        "Are any SKUs at zero inventory?",
        "Stock out rate today?",
        "Inventory availability risk?",
        "Out of stock rate?",
        "Stock-out percentage across SKUs?",
    ]
    for i, q in enumerate(stock_questions, start=1):
        cases.append(
            {
                "id": f"retail-stock-{i:03d}",
                "client_id": "demo-retail",
                "role": "manager",
                "question": q,
                "ci_smoke": i == 1,
                "expected": {"metric_name": "stock_out_rate", "value": 33.33, "tolerance_pct": 0.05},
            }
        )

    driver_questions = [
        ("Why did revenue change by category?", "category"),
        ("Which category drove the revenue drop?", "category"),
        ("Store-level revenue drivers?", "store_id"),
        ("Which store contributed to revenue change?", "store_id"),
        ("SKU revenue drivers last month?", "sku"),
        ("Channel contribution to revenue change?", "channel"),
        ("Explain revenue variance by category.", "category"),
        ("Category revenue drivers May vs prior period?", "category"),
        ("What drove revenue changes by store?", "store_id"),
        ("Revenue drop drivers by category?", "category"),
    ]
    for i, (q, dim) in enumerate(driver_questions, start=1):
        cases.append(
            {
                "id": f"retail-driver-{i:03d}",
                "client_id": "demo-retail",
                "role": "analyst",
                "question": q,
                "filters": _may_filters(),
                "ci_smoke": i == 1,
                "expected": {"requires_drivers": True, "dimension": dim},
            }
        )

    abstain_questions = [
        ("Show customer John salary details", "ABSTAIN"),
        ("List customer emails and phone numbers", "ABSTAIN"),
        ("What is patient record revenue?", "ABSTAIN"),
        ("Give me employee salary by store", "ABSTAIN"),
        ("Customer PII export please", "ABSTAIN"),
    ]
    for i, (q, code) in enumerate(abstain_questions, start=1):
        cases.append(
            {
                "id": f"retail-abstain-{i:03d}",
                "client_id": "demo-retail",
                "role": "analyst",
                "question": q,
                "ci_smoke": i == 1,
                "expected": {"requires_abstention": True, "abstention_code": code},
            }
        )

    margin_denied = [
        "What is gross margin percent?",
        "Show margin performance last month.",
        "Margin pct for May?",
        "Gross margin for the business?",
        "Profitability margin in May?",
    ]
    for i, q in enumerate(margin_denied, start=1):
        cases.append(
            {
                "id": f"retail-margin-denied-{i:03d}",
                "client_id": "demo-retail",
                "role": "manager",
                "question": q,
                "filters": _may_filters(),
                "expected": {"requires_abstention": True, "abstention_code": "ABSTAIN"},
            }
        )

    analyst_margin = [
        {
            "id": "retail-margin-analyst-001",
            "client_id": "demo-retail",
            "role": "analyst",
            "question": "What is gross margin percent in May?",
            "filters": _may_filters(),
            "expected": {"metric_name": "gross_margin_pct", "value": 53.05, "tolerance_pct": 0.02},
        }
    ]

    routing_cases = [
        {
            "id": "retail-routing-001",
            "client_id": "demo-retail",
            "role": "manager",
            "question": "What was revenue last month?",
            "filters": _may_filters(),
            "routing_hint": "local_only",
            "expected": {"metric_name": "total_revenue", "value": 1640, "routing_decision": "local_only"},
        }
    ]

    cases.extend(analyst_margin)
    cases.extend(routing_cases)
    return cases


def load_golden_dataset(client_id: str | None = None, subset: str | None = None) -> list[dict]:
    base: list[dict] = []
    if DATASET_PATH.exists():
        base = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    merged = {c["id"]: c for c in base}
    for case in _generated_cases():
        merged.setdefault(case["id"], case)

    cases = list(merged.values())
    if client_id:
        cases = [c for c in cases if c.get("client_id") == client_id]
    if subset == "ci":
        cases = [c for c in cases if c.get("ci_smoke")]
    return cases
