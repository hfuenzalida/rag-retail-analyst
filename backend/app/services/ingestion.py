"""CSV schema mapping and data loading."""

import csv
import io
from datetime import datetime
from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb

from app.models.ingest import CsvConfirmRequest, FieldMapping, MappingSuggestion, TableName

TABLE_FIELDS: dict[TableName, dict[str, dict[str, Any]]] = {
    "sales": {
        "sale_id": {"required": True, "aliases": ["sale_id", "transaction_id", "order_id"]},
        "sale_date": {"required": True, "aliases": ["sale_date", "solddate", "date", "transaction_date"]},
        "store_id": {"required": False, "aliases": ["store_id", "store", "location_id"]},
        "channel": {"required": False, "aliases": ["channel", "sales_channel"]},
        "customer_segment": {"required": False, "aliases": ["customer_segment", "segment"]},
        "sku": {"required": True, "aliases": ["sku", "itemcode", "product_code", "product_sku"]},
        "quantity": {"required": True, "aliases": ["quantity", "qty", "units"]},
        "unit_price": {"required": True, "aliases": ["unit_price", "price", "unitprice"]},
        "discount": {"required": False, "aliases": ["discount", "discount_amount"]},
        "gross_revenue": {"required": False, "aliases": ["gross_revenue", "gross", "gross_amount"]},
        "net_revenue": {"required": False, "aliases": ["net_revenue", "net", "revenue", "amount"]},
    },
    "inventory": {
        "sku": {"required": True, "aliases": ["sku", "itemcode", "product_code"]},
        "location": {"required": True, "aliases": ["location", "store_id", "warehouse"]},
        "on_hand_qty": {"required": True, "aliases": ["on_hand_qty", "onhand", "qty_on_hand", "quantity"]},
        "reserved_qty": {"required": False, "aliases": ["reserved_qty", "reserved"]},
        "reorder_point": {"required": False, "aliases": ["reorder_point", "reorder_level"]},
        "lead_time_days": {"required": False, "aliases": ["lead_time_days", "lead_time"]},
    },
    "products": {
        "sku": {"required": True, "aliases": ["sku", "itemcode", "product_code"]},
        "category": {"required": False, "aliases": ["category", "product_category"]},
        "brand": {"required": False, "aliases": ["brand", "manufacturer"]},
        "unit_cost": {"required": False, "aliases": ["unit_cost", "cost"]},
        "unit_price": {"required": True, "aliases": ["unit_price", "price", "retail_price"]},
        "margin_pct": {"required": False, "aliases": ["margin_pct", "margin", "margin_percent"]},
        "status": {"required": False, "aliases": ["status", "active"]},
    },
}


def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def propose_csv_mapping(
    client_id: str,
    table_name: TableName,
    headers: list[str],
    sample_rows: list[list[str]],
) -> MappingSuggestion:
    """Rule-based column mapping proposal (human confirmation required before load)."""
    del sample_rows  # reserved for future type inference
    schema = TABLE_FIELDS[table_name]
    normalized_headers = {_normalize(h): h for h in headers}
    mappings: list[FieldMapping] = []
    used_sources: set[str] = set()
    warnings: list[str] = []

    for target_field, spec in schema.items():
        matched_header = None
        confidence = 0.0
        for alias in spec["aliases"]:
            if alias in normalized_headers:
                matched_header = normalized_headers[alias]
                confidence = 1.0 if alias == target_field else 0.9
                break
        if matched_header:
            mappings.append(
                FieldMapping(
                    source_column=matched_header,
                    target_field=target_field,
                    confidence=confidence,
                    required=spec["required"],
                )
            )
            used_sources.add(_normalize(matched_header))

    unmapped = [h for h in headers if _normalize(h) not in used_sources]
    mapped_targets = {m.target_field for m in mappings}
    missing_required = [
        field
        for field, spec in schema.items()
        if spec["required"] and field not in mapped_targets
    ]
    if unmapped:
        warnings.append(f"Unmapped columns will be ignored: {', '.join(unmapped)}")
    if missing_required:
        warnings.append(f"Missing required fields: {', '.join(missing_required)}")

    return MappingSuggestion(
        client_id=client_id,
        table_name=table_name,
        mappings=mappings,
        unmapped_columns=unmapped,
        missing_required_fields=missing_required,
        warnings=warnings,
    )


def _parse_value(field: str, raw: str) -> Any:
    raw = raw.strip()
    if raw == "":
        return None
    if field in {"quantity", "on_hand_qty", "reserved_qty", "reorder_point", "lead_time_days"}:
        return int(float(raw))
    if field in {"unit_price", "unit_cost", "discount", "gross_revenue", "net_revenue", "margin_pct"}:
        return float(raw)
    if field == "sale_date":
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Invalid date format for sale_date: {raw}")
    return raw


def _row_dict(headers: list[str], row: list[str], mappings: list[FieldMapping]) -> dict[str, Any]:
    header_index = {h: idx for idx, h in enumerate(headers)}
    mapped: dict[str, Any] = {}
    for mapping in mappings:
        idx = header_index.get(mapping.source_column)
        if idx is None or idx >= len(row):
            continue
        mapped[mapping.target_field] = _parse_value(mapping.target_field, row[idx])
    return mapped


def save_proposed_mapping(conn: Connection, suggestion: MappingSuggestion) -> None:
    conn.execute(
        """
        INSERT INTO csv_mappings (client_id, table_name, mapping, status)
        VALUES (%s, %s, %s, 'proposed')
        ON CONFLICT (client_id, table_name)
        DO UPDATE SET mapping = EXCLUDED.mapping, status = 'proposed', updated_at = NOW()
        """,
        [
            suggestion.client_id,
            suggestion.table_name,
            Jsonb(suggestion.model_dump()),
        ],
    )


def load_csv_rows(conn: Connection, request: CsvConfirmRequest) -> int:
    if request.mappings and any(m.confidence < 0.5 for m in request.mappings):
        raise ValueError("Low-confidence mappings require human review before confirm.")

    inserted = 0
    for row in request.rows:
        data = _row_dict(request.headers, row, request.mappings)
        data["client_id"] = request.client_id
        if request.table_name == "sales":
            _insert_sales_row(conn, data)
        elif request.table_name == "inventory":
            _insert_inventory_row(conn, data)
        else:
            _insert_products_row(conn, data)
        inserted += 1

    conn.execute(
        """
        INSERT INTO csv_mappings (client_id, table_name, mapping, status)
        VALUES (%s, %s, %s, 'confirmed')
        ON CONFLICT (client_id, table_name)
        DO UPDATE SET mapping = EXCLUDED.mapping, status = 'confirmed', updated_at = NOW()
        """,
        [
            request.client_id,
            request.table_name,
            Jsonb({"mappings": [m.model_dump() for m in request.mappings]}),
        ],
    )
    conn.commit()
    return inserted


def _insert_sales_row(conn: Connection, data: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO sales (
            sale_id, client_id, sale_date, store_id, channel, customer_segment,
            sku, quantity, unit_price, discount, gross_revenue, net_revenue
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (sale_id) DO UPDATE SET
            sale_date = EXCLUDED.sale_date,
            quantity = EXCLUDED.quantity,
            net_revenue = EXCLUDED.net_revenue
        """,
        [
            data.get("sale_id"),
            data["client_id"],
            data.get("sale_date"),
            data.get("store_id"),
            data.get("channel"),
            data.get("customer_segment"),
            data.get("sku"),
            data.get("quantity"),
            data.get("unit_price"),
            data.get("discount") or 0,
            data.get("gross_revenue"),
            data.get("net_revenue"),
        ],
    )


def _insert_inventory_row(conn: Connection, data: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO inventory (
            client_id, sku, location, on_hand_qty, reserved_qty, reorder_point, lead_time_days
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (client_id, sku, location) DO UPDATE SET
            on_hand_qty = EXCLUDED.on_hand_qty,
            reserved_qty = EXCLUDED.reserved_qty
        """,
        [
            data["client_id"],
            data.get("sku"),
            data.get("location"),
            data.get("on_hand_qty"),
            data.get("reserved_qty") or 0,
            data.get("reorder_point"),
            data.get("lead_time_days"),
        ],
    )


def _insert_products_row(conn: Connection, data: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO products (
            sku, client_id, category, brand, unit_cost, unit_price, margin_pct, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (sku) DO UPDATE SET
            category = EXCLUDED.category,
            unit_cost = EXCLUDED.unit_cost,
            unit_price = EXCLUDED.unit_price
        """,
        [
            data.get("sku"),
            data["client_id"],
            data.get("category"),
            data.get("brand"),
            data.get("unit_cost"),
            data.get("unit_price"),
            data.get("margin_pct"),
            data.get("status") or "active",
        ],
    )


def parse_csv_text(content: str) -> tuple[list[str], list[list[str]]]:
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty")
    headers = rows[0]
    data_rows = rows[1:]
    return headers, data_rows
