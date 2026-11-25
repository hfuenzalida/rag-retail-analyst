-- Base schema for retail metrics and RAG (Phase 1+ will populate migrations)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    category TEXT,
    brand TEXT,
    unit_cost NUMERIC(12, 2),
    unit_price NUMERIC(12, 2),
    margin_pct NUMERIC(6, 2),
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    sale_date DATE NOT NULL,
    store_id TEXT,
    channel TEXT,
    customer_segment TEXT,
    sku TEXT REFERENCES products (sku),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2),
    discount NUMERIC(12, 2) DEFAULT 0,
    gross_revenue NUMERIC(14, 2),
    net_revenue NUMERIC(14, 2)
);

CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    client_id TEXT NOT NULL,
    sku TEXT REFERENCES products (sku),
    location TEXT NOT NULL,
    on_hand_qty INTEGER NOT NULL DEFAULT 0,
    reserved_qty INTEGER NOT NULL DEFAULT 0,
    reorder_point INTEGER,
    lead_time_days INTEGER,
    UNIQUE (client_id, sku, location)
);

CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    client_id TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384)
);

CREATE INDEX IF NOT EXISTS idx_sales_client_date ON sales (client_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_inventory_client_sku ON inventory (client_id, sku);
CREATE INDEX IF NOT EXISTS idx_rag_documents_client ON rag_documents (client_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_metadata ON rag_documents USING gin (metadata);
CREATE INDEX IF NOT EXISTS idx_rag_documents_content_fts ON rag_documents USING gin (to_tsvector('english', content));

CREATE TABLE IF NOT EXISTS csv_mappings (
    id SERIAL PRIMARY KEY,
    client_id TEXT NOT NULL,
    table_name TEXT NOT NULL,
    mapping JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (client_id, table_name)
);
