"""Intent classification tests."""

from datetime import date

from app.models.query_models import DateRange, QueryFilters, QueryRequest
from app.services.intent import classify_intent


def test_intent_revenue():
    intent = classify_intent(
        QueryRequest(question="What was total net revenue last month?", client_id="demo-retail")
    )
    assert "total_revenue" in intent.metrics


def test_intent_stock_out():
    intent = classify_intent(
        QueryRequest(question="Which SKUs are currently out of stock?", client_id="demo-retail")
    )
    assert intent.metrics == ["stock_out_rate"]


def test_intent_manager_denied_margin():
    intent = classify_intent(
        QueryRequest(
            question="What is our gross margin percent?",
            client_id="demo-retail",
            role="manager",
        )
    )
    assert intent.abstain_reason is not None


def test_intent_driver_analysis():
    intent = classify_intent(
        QueryRequest(
            question="Which category contributed most to the revenue drop?",
            client_id="demo-retail",
            role="analyst",
            filters=QueryFilters(
                date_range=DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
            ),
        )
    )
    assert intent.driver_dimension == "category"
    assert intent.driver_metric == "total_revenue"
