"""Filter helper tests."""

from datetime import date

from app.db.filters import prior_window, sales_filters
from app.models.query_models import DateRange, QueryFilters


def test_prior_window_same_length():
    window = DateRange(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))
    prior = prior_window(window)
    span = (window.end_date - window.start_date).days + 1
    prior_span = (prior.end_date - prior.start_date).days + 1
    assert span == prior_span == 31
    assert prior.end_date == date(2026, 4, 30)
    assert prior.start_date == date(2026, 3, 31)


def test_sales_filters_include_category():
    filters = QueryFilters(category="Shoes")
    sf = sales_filters("demo-retail", filters)
    assert "category = %s" in sf.clause
    assert sf.params[-1] == "Shoes"
