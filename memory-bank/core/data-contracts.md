# Data Contracts

## sales

| Column | Type | Required |
|--------|------|----------|
| sale_id | text | yes |
| client_id | text | yes |
| sale_date | date | yes |
| store_id | text | no |
| channel | text | no |
| customer_segment | text | no |
| sku | text | yes |
| quantity | integer | yes |
| unit_price | numeric | yes |
| discount | numeric | default 0 |
| gross_revenue | numeric | no |
| net_revenue | numeric | no |

## inventory

| Column | Type | Required |
|--------|------|----------|
| client_id | text | yes |
| sku | text | yes |
| location | text | yes |
| on_hand_qty | integer | yes |
| reserved_qty | integer | default 0 |
| reorder_point | integer | no |
| lead_time_days | integer | no |

## products

| Column | Type | Required |
|--------|------|----------|
| sku | text | yes (PK) |
| client_id | text | yes |
| category | text | no |
| brand | text | no |
| unit_cost | numeric | no |
| unit_price | numeric | no |
| margin_pct | numeric | no |
| status | text | default active |

## CSV Mapping

- Admin confirms agent-proposed mappings before persistence.
- Common aliases: `ItemCode` → `sku`, `SoldDate` → `sale_date`.

## rag_documents

- `client_id`, `content`, `metadata` (jsonb), `embedding` (vector)
