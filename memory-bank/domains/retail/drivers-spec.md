# Drivers Spec (v1)

`get_top_drivers` uses **descriptive group-by deltas**:

- Compare metric in window A vs prior window B
- Rank dimensions (category, store_id, sku) by contribution to change
- Return top N with plain-language descriptions

Advanced modeling (regression, SHAP) deferred to v2.
