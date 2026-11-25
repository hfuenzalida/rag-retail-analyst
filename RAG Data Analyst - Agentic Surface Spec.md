# Agentic Surface Spec: API + Tools for Retail RAG Data Analyst

_Based on your completed question sheet and preferences for the RAG Data Analyst suite._[file:141]

---

## 1. Core HTTP API Surface

### 1.1 Primary Entry Point

- **Endpoint**: `POST /query`
- **Purpose**: Single generic entry point for all analytical questions (inventory, sales, risk, etc.).
- **Behavior**:
  - Accepts a natural‑language question plus optional filters and routing hints.
  - Internally routes to the appropriate workflow (inventory, sales, forecasting) based on question and filters.

### 1.2 Request Payload (Pydantic Model)

`QueryRequest` (strict Pydantic model):

- `question: str`
  - NL question from user (manager or analyst).
- `detail_level: Literal["summary", "deep_dive"]`
  - Controls answer granularity instead of separate endpoints or response types.
- `mode: Literal["manager", "analyst"]`
  - Used for UX tone and allowed tools (manager = lower privilege).
- `filters: Optional[QueryFilters]`
  - `date_range: Optional[DateRange]`
    - `start_date: date`
    - `end_date: date`
  - `store_id: Optional[str]`
  - `category: Optional[str]`
  - `sku: Optional[str]`
- `routing_hint: Optional[Literal["local_only", "hybrid", "cloud_assist"]]`
  - Client or UI can force routing behavior if needed.
- `client_id: str`
  - Required for all requests, even in single‑tenant v1, to keep multi‑tenancy extensible.[file:141]
- `role: Literal["manager", "analyst", "admin"]`
  - Redundant with `mode` but explicit for backend permissions enforcement.

All fields are validated by Pydantic; invalid requests return structured errors.

### 1.3 Response Payload (Pydantic Model)

`QueryResponse`:

- `summary: str`
  - High‑level narrative answer tuned by `detail_level` and `mode`.
- `metrics: List[Metric]`
  - `name: str`
  - `value: Decimal`
  - `unit: Optional[str]`
  - `time_window: Optional[DateRange]`
  - `context: Optional[str]` (e.g., “store A, category shoes”).
- `drivers: List[Driver]`
  - `dimension: str` (e.g., `category`, `store_id`, `sku`)
  - `impact: Decimal` (positive/negative contribution)
  - `description: str` (plain‑language explanation).
- `recommendations: List[Action]`
  - `label: str` (short action name)
  - `description: str`
  - `priority: Literal["low", "medium", "high"]`
  - `type: Literal["inventory", "pricing", "promotion", "other"]`
- `citations: List[Citation]`
  - `type: Literal["data", "document"]`
  - `source: str` (e.g., table/view name or doc id)
  - `reference: str` (e.g., row key, doc section).
- `confidence: float`
  - model‑level confidence in 0–1 range.
- `routing_decision: Literal["local_only", "cloud_assist", "cloud_only"]`
  - actual routing decision taken for this request.
- `error: Optional[ErrorInfo]`
  - `code: str`
  - `message: str`
  - `retry_hint: Optional[str]`

Strict models ensure the AI must conform to the schema before responses reach the frontend or downstream systems.[file:141]

---

## 2. Data Tools Surface (SQL / Metrics)

The RAG Analyst agent interacts with **pre‑defined metric tools only** in v1; raw SQL is not exposed to the agent.[file:141]

### 2.1 Metric Tools

Exposed tools (Python functions with decorators):

1. `run_metric_query(metric_name: str, filters: QueryFilters) -> MetricResult`
   - Examples of `metric_name`:
     - `total_revenue`
     - `units_sold`
     - `stock_out_rate`
     - `gross_margin_pct`
   - Internally maps to vetted SQL/DB logic; returns clean metric objects.

2. `get_top_drivers(metric_name: str, dimension: str, window: DateRange) -> List[Driver]`
   - Computes contribution by dimension (e.g., category, store) using standardized driver‑analysis logic.

3. (Optional v1.5) `get_metric_timeseries(metric_name: str, filters: QueryFilters, granularity: str) -> TimeSeriesResult`
   - For trend plots and deep‑dive answers.

**Agent constraints:**

- Agent cannot call arbitrary SQL.
- All metric tools are permission‑checked: managers may access only approved metrics; advanced or sensitive metrics can be restricted to analysts/admins.

---

## 3. RAG Tools Surface (Documents & Schema Context)

RAG tools expose local document and schema knowledge to the agent.

### 3.1 Retrieval Tools

1. `search_docs(text_query: str, k: int, filters: DocFilters) -> List[DocChunk]`
   - Hybrid vector + keyword search over local RAG index.
   - `DocFilters` can include:
     - `client_id`
     - `doc_type` (e.g., `report`, `playbook`, `note`)
     - `date_range`

2. `get_schema_docs(table_or_metric_name: str) -> List[DocChunk]`
   - Returns documentation chunks describing:
     - table schema,
     - metric definitions,
     - business rules.

These are used to ground explanations (“margin is calculated as X”) and prevent metric misunderstandings.

### 3.2 Write‑Back Tools (Optional / Guarded)

3. `create_playbook_entry(title: str, body: str, tags: List[str]) -> PlaybookEntry`
   - Agent can propose reusable analyses or explanations.
   - Must be guarded:
     - only analysts/admins can approve and persist entries.
     - managers cannot trigger this tool.

In v1, this can be **suggest‑only**: agent drafts playbook entries; a human approves via UI.

---

## 4. Routing & Privacy Tools (Local vs Cloud)

Routing logic must explicitly distinguish **sensitive** vs **generic** tasks.[file:141]

### 4.1 Sensitivity Check

`check_sensitivity(prompt: str, context: Optional[ContextSummary]) -> SensitivityResult`

- Returns:
  - `level: Literal["low", "medium", "high"]`
  - `reasons: List[str]` (e.g., “contains PII”, “raw transaction IDs”).
- Implementation:
  - Local classifier (rule‑based + ML) that inspects prompt and context.
- Policy:
  - `high` → enforce `local_only`.
  - `medium` → apply sanitization + possibly `hybrid`.
  - `low` → cloud‑assist allowed, subject to client config.

### 4.2 Cloud Routing Tool

`route_to_cloud_llm(task_description: str, sanitized_payload: Any) -> CloudLLMResult`

- Always receives **sanitized** payload:
  - aggregated metrics,
  - text that does not contain identifiable customer-level data.
- Used for:
  - complex reasoning on summaries,
  - template generation (emails, reports),
  - general explanatory content.

Routing decision is recorded in `routing_decision` in `QueryResponse`.

---

## 5. Evaluation & Safety Tools (Separate Evaluator Agent)

Evaluation is executed by a **separate evaluator agent or backend hook**, not inline self‑critique in the same loop to avoid latency and cost.[file:141]

### 5.1 Faithfulness and Relevance

1. `evaluate_answer_faithfulness(answer: QueryResponse, context: RetrievalBundle) -> EvalScore`
   - Checks whether claims are supported by metrics and RAG context.
2. `evaluate_answer_relevance(answer: QueryResponse, question: QueryRequest) -> EvalScore`
   - Ensures the answer is on‑topic and non‑hedged.

### 5.2 Golden Question Runner

`run_golden_eval(client_id: str) -> GoldenEvalReport`

- Triggered via `/eval/run`.
- Runs pre‑defined “golden questions” and compares outputs to known baselines.
- Used to detect regressions when:
  - models change,
  - prompts are updated,
  - routing logic is tuned.[file:141]

---

## 6. Utility Tools

### 6.1 Visualization Spec Generator

`generate_chart_spec(metrics: List[Metric], chart_type: str) -> ChartSpec`

- Returns JSON spec consumable by frontend (e.g., Vega/Plotly config).
- This can be a backend utility or a simple agent tool; in either case it produces deterministic specs from metric data.

### 6.2 Notification / Report Formatter

`format_email_notification(summary: str, actions: List[Action]) -> EmailDraft`

- Generates manager‑friendly email copy.
- Preferably executed via **cloud LLM** with sanitized content only.
- Can be exposed as a separate endpoint (`/compose/email`) or as an internal tool.

---

## 7. Ingestion & Admin Surface (Non-Chat Tools)

### 7.1 Admin-Only Ingestion Endpoints

1. `POST /ingest/csv`
   - Uploads CSV files for `sales`, `inventory`, `products`.
   - Admin‑only, requires `role="admin"` and proper auth.[file:141]

2. `POST /ingest/db-config`
   - Registers or updates DB connection info for a client.
   - Admin‑only; not exposed to agents in v1.

### 7.2 Schema Mapping Tool

`map_csv_to_schema(sample_rows: CsvSample, client_id: str) -> MappingSuggestion`

- Agent suggests column mappings (e.g., `"ItemCode" -> sku`, `"SoldDate" -> sale_date`).
- Must be **confirmed by a human in the UI** before being persisted.[file:141]
- A UI flow:
  - Agent proposes mapping.
  - Admin reviews and clicks “Confirm”.
  - Backend writes mapping to config store.

### 7.3 Config Management Tools

Config changes are backend‑enforced, not agent‑freeform:

- `update_thresholds(client_id, thresholds)` – only admin allowed.
- `update_default_windows(client_id, windows)` – admin or analyst.
- `update_hierarchies(client_id, hierarchy_config)` – admin.

Agent may **suggest** changes but cannot directly apply them; backend checks role and explicitly gates these operations.[file:141]

---

## 8. Auth, Tenancy, and Role Enforcement

### 8.1 Authentication & Tokens

- RAG endpoints require an auth token/session.
- Token carries:
  - `client_id`
  - `user_id`
  - `role` (`manager`, `analyst`, `admin`).

### 8.2 Role-Based Access Control

- RBAC enforced **at backend tool level**, not by the LLM itself.[file:141]
- Examples:
  - Managers:
    - can call `/query` with approved metrics.
    - cannot call ingestion endpoints or config tools.
  - Analysts:
    - can access more metrics and deep‑dive answers.
  - Admins:
    - can call ingestion, mapping, and config endpoints.

Tool decorators check `role` before execution; blocked calls never reach the LLM.

### 8.3 Tenancy

- Every tool and API call requires a `client_id`.
- Even in single‑tenant v1, keeping `client_id` in tool signatures avoids multi‑tenant retrofit pain.[file:141]

---

## 9. Error, Logging, and Observability Surface

### 9.1 Structured Error Model

`ErrorInfo`:

- `code: str` (e.g., `DATA_MISSING`, `ROUTING_FAILED`, `INVALID_FILTERS`).
- `message: str` (human‑readable).
- `retry_hint: Optional[str]` (e.g., “Try narrowing the date range.”).[file:141]

Errors are included in `QueryResponse.error`; the UI can:

- show the message,
- propose retry steps,
- avoid freezing or generic “something went wrong” messages.

### 9.2 Observability Endpoints

- `POST /eval/run`
  - Runs golden question evaluations for a given `client_id`.[file:141]
- `GET /metrics`
  - Exposes Prometheus‑style metrics (request counts, latency, error rates).
- Logging:
  - Standard backend logging (no explicit `log_event` tool required in v1).
  - Logs include routing decisions, sensitivity levels, and evaluation scores.

---

## 10. Implementation Preferences (FastAPI + Pydantic AI + YAML)

### 10.1 Framework Stack

- **Backend**: FastAPI (async, type‑safe).
- **Agent Framework**: Pydantic AI for:
  - structured agent outputs,
  - type‑checked tools,
  - easy integration with FastAPI.[file:141][web:122][web:130]

### 10.2 Tool Declaration Style

- **Execution logic**:
  - Implemented as clean Python functions with decorators (Pydantic AI tools).[web:130][web:133]
- **Agent configuration (prompts, role rules, routing boundaries)**:
  - Stored in **YAML files**:
    - `agents/rag_analyst.yaml`
    - `agents/evaluator.yaml`
    - `agents/ingestion.yaml`
  - YAML includes:
    - system prompts,
    - allowed tools list,
    - routing + sensitivity policies.

This separation lets vibe‑coding agents modify prompts and tool wiring via YAML while core execution logic remains stable.[file:141][web:132][web:137]

---

## 11. Open Questions to Finalize the Agentic Surface

To refine this spec further and prepare `AGENT_SURFACE.md` + a skeleton repo, it would help to clarify:

1. **Metric taxonomy**
   - Do you have a list of canonical metric names and their exact formulas (e.g., `total_revenue`, `net_revenue`, `margin_pct`, `stock_out_rate`) you want encoded in `run_metric_query`, or should we define a default retail core and leave extension points?

2. **Driver analysis method**
   - Should `get_top_drivers` be:
     - purely descriptive (group‑by deltas, contribution analysis),
     - or use a specific modeling approach (e.g., regression, SHAP on a model)?

3. **Playbook write‑back**
   - For `create_playbook_entry`, do you want this active in v1 (with human approval), or reserved for v2 so v1 focuses only on answering questions?

4. **Cloud LLM set**
   - Which cloud LLM(s) do you want wired by default for `route_to_cloud_llm` (e.g., Claude, Gemini, OpenAI), and do you want per‑client configuration via YAML?

5. **Visualization standard**
   - Should `generate_chart_spec` target a specific frontend library (e.g., Plotly, ECharts, Vega‑Lite), or remain abstract with a generic spec format?

6. **Golden question source**
   - Do you already have a candidate set of golden questions for retail analytics, or should we design a base set (e.g., 10–20 core questions) together?

If you answer these, I can produce a final `AGENT_SURFACE.md` plus a FastAPI + Pydantic AI skeleton that matches your architecture and is ready to vibe‑code against.
