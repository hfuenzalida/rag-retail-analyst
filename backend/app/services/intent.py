"""Rule-based question intent classification for tool selection."""

import re
from dataclasses import dataclass
from datetime import date, timedelta

from app.models.query_models import DateRange, QueryFilters, QueryRequest


@dataclass
class QueryIntent:
    metrics: list[str]
    driver_dimension: str | None = None
    driver_metric: str | None = None
    schema_lookup: str | None = None
    doc_search: str | None = None
    abstain_reason: str | None = None


def _effective_filters(request: QueryRequest) -> QueryFilters:
    if request.filters:
        return request.filters
    end = date.today()
    return QueryFilters(date_range=DateRange(start_date=end - timedelta(days=30), end_date=end))


def _driver_window(filters: QueryFilters) -> DateRange:
    if filters.date_range:
        return filters.date_range
    end = date.today()
    return DateRange(start_date=end - timedelta(days=30), end_date=end)


def classify_intent(request: QueryRequest) -> QueryIntent:
    q = request.question.lower()

    if re.search(r"\b(customer|salary|patient)\b", q):
        return QueryIntent(metrics=[], abstain_reason="Question appears to involve sensitive PII — cannot answer from available retail metrics.")

    if re.search(r"\b(stock.?out|out of stock|inventory risk|reorder)\b", q):
        return QueryIntent(
            metrics=["stock_out_rate"],
            doc_search="stock out inventory risk",
            schema_lookup="stock_out_rate",
        )

    if re.search(r"\b(margin|profitability)\b", q):
        if request.role == "manager":
            return QueryIntent(metrics=[], abstain_reason="Gross margin metrics require analyst or admin role.")
        if re.search(r"\b(driver|contribut|which category|why)\b", q):
            return QueryIntent(
                metrics=["gross_margin_pct"],
                driver_metric="total_revenue",
                driver_dimension="category",
                schema_lookup="gross_margin_pct",
            )
        return QueryIntent(metrics=["gross_margin_pct"], schema_lookup="gross_margin_pct")

    if re.search(r"\b(driver|contribut|why|drop|decline|change|variance)\b", q):
        dimension = "category"
        if "store" in q:
            dimension = "store_id"
        if "sku" in q:
            dimension = "sku"
        if "channel" in q:
            dimension = "channel"
        return QueryIntent(
            metrics=["total_revenue"],
            driver_metric="total_revenue",
            driver_dimension=dimension,
            schema_lookup="total_revenue",
        )

    if re.search(r"\b(units sold|quantity|units)\b", q):
        return QueryIntent(metrics=["units_sold"], schema_lookup="units_sold")

    if re.search(r"\b(revenue|sales)\b", q):
        return QueryIntent(metrics=["total_revenue"], schema_lookup="total_revenue")

    if re.search(r"\b(schema|table|metric definition|how is .* calculated)\b", q):
        target = "sales"
        for name in ("total_revenue", "inventory", "products", "stock_out_rate", "units_sold"):
            if name.replace("_", " ") in q or name in q:
                target = name
                break
        return QueryIntent(metrics=[], schema_lookup=target)

    return QueryIntent(
        metrics=["total_revenue"],
        schema_lookup="total_revenue",
        abstain_reason=None,
    )


def effective_filters(request: QueryRequest) -> QueryFilters:
    return _effective_filters(request)


def driver_window(request: QueryRequest) -> DateRange:
    return _driver_window(_effective_filters(request))
