"""Demo retail seed data for local development and evals."""

from psycopg import Connection

from app.db.rag_repository import ingest_text_document
from app.rag.schema_docs import schema_doc_requests

CLIENT_ID = "demo-retail"

PRODUCTS = [
    ("SHOE-001", "Shoes", "TrailCo", 40, 80),
    ("SHIRT-001", "Apparel", "SoftWear", 15, 35),
    ("SHOE-002", "Shoes", "TrailCo", 50, 100),
]

APRIL_SALES = [
    ("sale-apr-001", "2026-04-05", "store-a", "in-store", "SHOE-001", 15, 80, 0, 1200, 1200),
    ("sale-apr-002", "2026-04-12", "store-a", "in-store", "SHIRT-001", 25, 35, 0, 875, 875),
    ("sale-apr-003", "2026-04-20", "store-b", "online", "SHOE-002", 10, 100, 0, 1000, 1000),
]

MAY_SALES = [
    ("sale-may-001", "2026-05-03", "store-a", "in-store", "SHOE-001", 8, 80, 0, 640, 640),
    ("sale-may-002", "2026-05-10", "store-a", "in-store", "SHIRT-001", 20, 35, 0, 700, 700),
    ("sale-may-003", "2026-05-18", "store-b", "online", "SHOE-002", 3, 100, 0, 300, 300),
]

INVENTORY = [
    ("SHOE-001", "store-a", 0, 0, 10, 7),
    ("SHIRT-001", "store-a", 50, 5, 20, 5),
    ("SHOE-002", "store-b", 5, 1, 8, 10),
]

# Documented expected values for golden-question validation
EXPECTED = {
    "may_2026_total_revenue": 1640,
    "april_2026_total_revenue": 3075,
    "stock_out_rate_pct": 33.33,
}


def clear_client_data(conn: Connection, client_id: str = CLIENT_ID) -> None:
    conn.execute("DELETE FROM rag_documents WHERE client_id = %s", [client_id])
    conn.execute("DELETE FROM csv_mappings WHERE client_id = %s", [client_id])
    conn.execute("DELETE FROM sales WHERE client_id = %s", [client_id])
    conn.execute("DELETE FROM inventory WHERE client_id = %s", [client_id])
    conn.execute("DELETE FROM products WHERE client_id = %s", [client_id])


def seed_demo_retail(conn: Connection, client_id: str = CLIENT_ID) -> None:
    clear_client_data(conn, client_id)

    for sku, category, brand, cost, price in PRODUCTS:
        margin = round((price - cost) / price * 100, 2)
        conn.execute(
            """
            INSERT INTO products (sku, client_id, category, brand, unit_cost, unit_price, margin_pct, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
            """,
            [sku, client_id, category, brand, cost, price, margin],
        )

    for row in APRIL_SALES + MAY_SALES:
        conn.execute(
            """
            INSERT INTO sales (
                sale_id, client_id, sale_date, store_id, channel, sku,
                quantity, unit_price, discount, gross_revenue, net_revenue
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [row[0], client_id, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]],
        )

    for sku, location, on_hand, reserved, reorder, lead in INVENTORY:
        conn.execute(
            """
            INSERT INTO inventory (
                client_id, sku, location, on_hand_qty, reserved_qty, reorder_point, lead_time_days
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [client_id, sku, location, on_hand, reserved, reorder, lead],
        )

    for doc in schema_doc_requests(client_id):
        ingest_text_document(
            conn,
            client_id=doc.client_id,
            content=doc.content,
            metadata={
                "doc_type": doc.doc_type,
                "title": doc.title,
                "tags": doc.tags,
            },
        )

    conn.commit()
