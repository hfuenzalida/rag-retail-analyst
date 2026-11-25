"""Built-in schema and metric documentation for RAG grounding."""

from app.models.rag import IngestDocumentRequest

SCHEMA_DOC_ENTRIES: list[dict] = [
    {
        "title": "sales table schema",
        "doc_type": "schema",
        "tags": ["sales", "schema"],
        "content": (
            "Table sales stores transaction line items. Required fields: sale_id, client_id, "
            "sale_date, sku, quantity, unit_price. Optional: store_id, channel, customer_segment, "
            "discount, gross_revenue, net_revenue. Join products on sku for category analysis."
        ),
    },
    {
        "title": "inventory table schema",
        "doc_type": "schema",
        "tags": ["inventory", "schema"],
        "content": (
            "Table inventory tracks on-hand stock by location. Required: client_id, sku, location, "
            "on_hand_qty. Optional: reserved_qty, reorder_point, lead_time_days. "
            "Stock-out occurs when on_hand_qty is zero or below."
        ),
    },
    {
        "title": "products table schema",
        "doc_type": "schema",
        "tags": ["products", "schema"],
        "content": (
            "Table products defines SKU master data. Required: sku, client_id. Optional: category, "
            "brand, unit_cost, unit_price, margin_pct, status (active/inactive)."
        ),
    },
    {
        "title": "total_revenue metric",
        "doc_type": "schema",
        "tags": ["metric", "total_revenue"],
        "content": (
            "Metric total_revenue equals SUM(net_revenue) from sales for the selected client_id "
            "and date window. Filters may include store_id, category (via products join), or sku."
        ),
    },
    {
        "title": "units_sold metric",
        "doc_type": "schema",
        "tags": ["metric", "units_sold"],
        "content": (
            "Metric units_sold equals SUM(quantity) from sales for the selected filters and date range."
        ),
    },
    {
        "title": "gross_margin_pct metric",
        "doc_type": "schema",
        "tags": ["metric", "gross_margin_pct"],
        "content": (
            "Metric gross_margin_pct is (SUM(net_revenue) - SUM(quantity * unit_cost)) / "
            "SUM(net_revenue) * 100 using sales joined to products. Analyst/admin role only."
        ),
    },
    {
        "title": "stock_out_rate metric",
        "doc_type": "schema",
        "tags": ["metric", "stock_out_rate"],
        "content": (
            "Metric stock_out_rate is the percentage of inventory rows where on_hand_qty <= 0 "
            "for the client. Point-in-time snapshot; not filtered by sale date."
        ),
    },
]


def schema_doc_requests(client_id: str) -> list[IngestDocumentRequest]:
    return [
        IngestDocumentRequest(
            client_id=client_id,
            content=entry["content"],
            doc_type=entry["doc_type"],
            title=entry["title"],
            tags=entry["tags"],
        )
        for entry in SCHEMA_DOC_ENTRIES
    ]
