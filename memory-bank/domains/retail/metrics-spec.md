# Retail Metrics Spec (v1 draft)

| Metric | Formula (draft) | Tables |
|--------|-----------------|--------|
| total_revenue | SUM(net_revenue) in window | sales |
| units_sold | SUM(quantity) in window | sales |
| gross_margin_pct | (SUM(net_revenue) - SUM(qty × unit_cost)) / SUM(net_revenue) × 100 | sales, products |
| stock_out_rate | rows with on_hand_qty ≤ 0 / total inventory rows × 100 | inventory |

Demo client (`demo-retail`) May 2026 total revenue = **1640**; stock-out rate = **33.33%**.
