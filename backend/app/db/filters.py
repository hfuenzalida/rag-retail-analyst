"""Shared SQL filter builder for client-scoped queries."""

from dataclasses import dataclass, field
from datetime import timedelta

from app.models.query_models import DateRange, QueryFilters


@dataclass
class SqlFilter:
    clause: str = ""
    params: list = field(default_factory=list)


def prior_window(window: DateRange) -> DateRange:
    span_days = (window.end_date - window.start_date).days + 1
    prior_end = window.start_date - timedelta(days=1)
    prior_start = prior_end - timedelta(days=span_days - 1)
    return DateRange(start_date=prior_start, end_date=prior_end)


def sales_filters(client_id: str, filters: QueryFilters | None, alias: str = "s") -> SqlFilter:
    a = alias
    result = SqlFilter(clause=f"{a}.client_id = %s", params=[client_id])
    if not filters:
        return result

    if filters.date_range:
        result.clause += f" AND {a}.sale_date >= %s AND {a}.sale_date <= %s"
        result.params.extend([filters.date_range.start_date, filters.date_range.end_date])
    if filters.store_id:
        result.clause += f" AND {a}.store_id = %s"
        result.params.append(filters.store_id)
    if filters.sku:
        result.clause += f" AND {a}.sku = %s"
        result.params.append(filters.sku)
    if filters.category:
        result.clause += (
            f" AND {a}.sku IN (SELECT sku FROM products WHERE client_id = %s AND category = %s)"
        )
        result.params.extend([client_id, filters.category])
    return result


def inventory_filters(client_id: str, filters: QueryFilters | None, alias: str = "i") -> SqlFilter:
    a = alias
    result = SqlFilter(clause=f"{a}.client_id = %s", params=[client_id])
    if not filters:
        return result
    if filters.sku:
        result.clause += f" AND {a}.sku = %s"
        result.params.append(filters.sku)
    if filters.store_id:
        result.clause += f" AND {a}.location = %s"
        result.params.append(filters.store_id)
    if filters.category:
        result.clause += (
            f" AND {a}.sku IN (SELECT sku FROM products WHERE client_id = %s AND category = %s)"
        )
        result.params.extend([client_id, filters.category])
    return result
