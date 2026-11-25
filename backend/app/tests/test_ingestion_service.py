"""CSV ingestion and mapping tests."""

from app.agents.ingestion_agent import map_csv_to_schema
from app.services.ingestion import _parse_value, _row_dict, parse_csv_text, propose_csv_mapping


def test_propose_mapping_aliases():
    suggestion = propose_csv_mapping(
        client_id="demo-retail",
        table_name="sales",
        headers=["ItemCode", "SoldDate", "Qty", "Net", "Store"],
        sample_rows=[["SHOE-001", "2026-06-01", "5", "400", "store-a"]],
    )
    mapped = {m.target_field: m.source_column for m in suggestion.mappings}
    assert mapped["sku"] == "ItemCode"
    assert mapped["sale_date"] == "SoldDate"
    assert mapped["quantity"] == "Qty"
    assert mapped["net_revenue"] == "Net"
    assert "sale_id" in suggestion.missing_required_fields


def test_map_csv_to_schema_agent_wrapper():
    suggestion = map_csv_to_schema(
        client_id="demo-retail",
        table_name="products",
        headers=["ItemCode", "category", "price"],
        sample_rows=[["SHOE-001", "Shoes", "80"]],
    )
    assert any(m.target_field == "sku" for m in suggestion.mappings)


def test_parse_csv_text():
    headers, rows = parse_csv_text("sku,qty\nA,1\nB,2\n")
    assert headers == ["sku", "qty"]
    assert rows == [["A", "1"], ["B", "2"]]


def test_row_dict_parsing():
    mappings = propose_csv_mapping(
        "demo-retail",
        "sales",
        ["SoldDate", "Qty"],
        [["2026-06-01", "3"]],
    ).mappings
    row = _row_dict(["SoldDate", "Qty"], ["2026-06-01", "3"], mappings)
    assert row["sale_date"].isoformat() == "2026-06-01"
    assert row["quantity"] == 3


def test_parse_value_date_formats():
    assert str(_parse_value("sale_date", "2026-06-01")) == "2026-06-01"
