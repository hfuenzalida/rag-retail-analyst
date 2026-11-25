# Agent Surface

## Primary Endpoint

`POST /query` — accepts `QueryRequest`, returns `QueryResponse`.

### QueryRequest

- `question`, `detail_level`, `mode`, `filters`, `routing_hint`, `client_id`, `role`

### QueryResponse

- `summary`, `metrics`, `drivers`, `recommendations`, `citations`, `confidence`, `routing_decision`, `error`

## Metric Tools (v1 — no raw SQL to agents)

- `run_metric_query(metric_name, filters) -> MetricResult`
- `get_top_drivers(metric_name, dimension, window) -> List[Driver]`

Canonical metrics: `total_revenue`, `units_sold`, `stock_out_rate`, `gross_margin_pct`.

## RAG Tools

- `search_docs(text_query, k, filters) -> List[DocChunk]`
- `get_schema_docs(table_or_metric_name) -> List[DocChunk]`

## Routing Tools

- `check_sensitivity(prompt, context) -> SensitivityResult`
- `route_to_cloud_llm(task_description, sanitized_payload) -> CloudLLMResult`

## Eval Tools

- `evaluate_answer_faithfulness`, `evaluate_answer_relevance`
- `run_golden_eval(client_id) -> GoldenEvalReport` via `POST /eval/run`

## RBAC

- **manager**: `/query` with approved metrics only
- **analyst**: extended metrics and deep_dive
- **admin**: ingestion and config endpoints

Enforced at tool decorator level, not by LLM.

## Admin Endpoints

- `POST /ingest/csv`, `POST /ingest/db-config` — admin only
