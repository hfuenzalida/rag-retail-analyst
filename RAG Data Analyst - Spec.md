# Spec: Sovereign RAG Data Analyst Suite for Retail Inventory & Sales (Vibe-Coded App)

## 1. Product Overview

### 1.1 Purpose

Build a **Sovereign AI RAG Data Analyst** that helps small retail businesses understand inventory and sales trends, answer ad‑hoc business questions, and generate decision‑ready explanations and recommendations based on their own data.[web:106][web:107]

### 1.2 Target Users

- **Primary users**: 
  - Retail owners and store managers (non‑technical business users).
  - Operations / data‑savvy staff (technical or semi‑technical users).
- The app must:
  - Provide **simple question interfaces** and structured answers for managers.
  - Allow **more advanced queries** and data views for technical staff.[web:107][web:43]

### 1.3 Domain and Scope (v1)

- **Domain**: Retail inventory and sales analytics.
- **Core questions** (examples):
  - “Why did sales drop last week compared to the previous week?”
  - “Which SKUs are at risk of stock‑out in the next 7 days?”
  - “What products drive most revenue but are often out of stock?”
  - “Which stores or channels have the best margin performance?”
- v1 focuses on **single business** setups; later versions may support multi‑tenant clients.

---

## 2. Data and Integration Spec (v1)

### 2.1 Required Data Sources

For v1 the suite MUST support:

- **Relational DB** (e.g., PostgreSQL/MySQL) with:
  - `sales` table (transactions, line items).
  - `inventory` table (on‑hand quantities, reorder levels).
  - `products` table (SKU, category, cost, price, attributes).
- **CSV / spreadsheets**:
  - historical sales exports,
  - supplier price lists,
  - ad‑hoc datasets uploaded by staff.

Only these sources are required for initial release; document stores and SaaS APIs can be added in later versions.[web:107][web:108]

### 2.2 Data Contracts (Logical Schema)

The spec expects **semantic tables**:

- `sales`:
  - `sale_id`, `sale_date`, `store_id`, `channel`, `customer_segment` (optional),
  - `sku`, `quantity`, `unit_price`, `discount`, `gross_revenue`, `net_revenue`.
- `inventory`:
  - `sku`, `location` (store, warehouse), `on_hand_qty`, `reserved_qty`, `reorder_point`, `lead_time_days`.
- `products`:
  - `sku`, `category`, `brand`, `unit_cost`, `unit_price`, `margin_pct`, `status` (active/inactive).

The RAG Analyst assumes these core entities exist and can be mapped from CSV/DB during onboarding.

---

## 3. Functional Capabilities

### 3.1 Core Capabilities

The suite must support:

1. **Question answering on inventory & sales**
   - User asks a natural‑language question.
   - System retrieves relevant data, computes KPIs, applies RAG context, and returns an answer.[web:40][web:107]

2. **Driver and root‑cause analysis**
   - Identify drivers of changes (sku, category, store, channel, promotion).
   - Explain why metrics changed (e.g., “Sales dropped due to fewer weekend visits and stock‑outs on top SKUs”).[web:40][web:43]

3. **Forecasting and risk detection (v1 light)**
   - Simple heuristics or lightweight models for:
     - stock‑out risk,
     - basic demand trends,
     - reorder suggestions (not full demand planning).[web:107]

4. **Recommendations and actions**
   - Suggest actions such as:
     - “Increase safety stock for SKU ABC.”
     - “Run promotion on slow‑moving category.”
     - “Rebalance inventory between stores.”[web:43]

5. **Evidence‑linked explanations**
   - Every important claim in answers must point to:
     - specific metrics (tables/plots),
     - specific RAG context (docs or notes when available),
     - or clearly state “no supporting data found.”[web:106][web:11]

### 3.2 User Journeys (v1)

- **Manager Journey**
  - Opens app → selects “Inventory & Sales Analyst”.
  - Asks question in plain language.
  - Receives:
    - short summary,
    - key metrics (charts or tables),
    - recommended actions,
    - citations to underlying data.[web:107][web:43]

- **Analyst/Ops Journey**
  - Uses advanced filters (time window, store, category).
  - Asks more technical questions (e.g., “Show contribution to margin by category for last quarter”).
  - Can drill down into detailed tables and configure thresholds (stock‑out risk, reorder points).

---

## 4. RAG and LLM Behavior Spec

### 4.1 Local RAG Behavior

- **Context**:
  - RAG uses only **local data and schema documentation** for grounding answers about inventory and sales.
- **Retrieval rules**:
  - Use hybrid vector + keyword search over:
    - metrics summaries,
    - playbooks and internal notes (if available later),
    - configuration docs.
- **Answer discipline**:
  - LLM must:
    - answer based only on retrieved context + computed metrics,
    - explicitly admit uncertainty when data is missing (“I don’t have enough data to answer this confidently.”),
    - never fabricate SKUs, customers, or numeric values.[web:106][web:107][web:11]

### 4.2 Cloud LLM Usage (Hybrid Mode)

- Cloud LLMs are allowed ONLY for:
  - generic explanations (“Explain what stock‑out means”),
  - communication templates (emails, reports) that do not expose raw PII or transaction rows.
- Cloud calls must:
  - receive aggregated or anonymized data (high‑level metrics),
  - be routed via the governance layer; sensitive prompts must be blocked.[web:106][web:115]

---

## 5. Non-Functional Requirements

### 5.1 Sovereignty and Privacy

- **Data residency**:
  - All transactional and inventory data remain on client infrastructure (local or private cloud).
- **No external storage of raw data**:
  - Cloud LLMs see only sanitized summaries as configured.
- **Auditability**:
  - Log all queries, routing decisions (local vs cloud), and model calls for audit and debugging.[web:106][web:93][web:115]

### 5.2 Performance

- Target response time:
  - < 5 seconds for typical questions on small datasets.
  - < 15 seconds for heavier queries (multi‑month data, complex drivers).

### 5.3 Reliability

- System must handle:
  - data source connectivity issues gracefully (clear error messages).
  - partial data (e.g., missing cost information) and call it out in answers rather than guessing.

---

## 6. UX and Interaction Requirements

### 6.1 UI Structure

- Main view:
  - **Question input** box.
  - **Filters** (date range, store, category).
  - **Answer panel** with sections:
    - Summary,
    - Metrics & visuals,
    - Drivers & explanations,
    - Recommended actions,
    - Citations & data links.[web:43][web:40]

### 6.2 Language and Tone

- Answers should be:
  - concise and business‑oriented,
  - free of jargon when addressing non‑technical users,
  - optionally include more technical detail when analyst mode is enabled.

### 6.3 Feedback Loop

- Users can:
  - thumbs‑up / thumbs‑down answers,
  - flag incorrect or hallucinated output,
  - request “Show me the data behind this statement”.

Feedback is logged for evaluation and future improvement.[web:11][web:122]

---

## 7. Safety and Hallucination Controls

### 7.1 Grounding Rules

- No “best guess” metrics: numeric outputs must always be derived from local DB or explicit input.
- If RAG retrieval returns poor or low‑confidence context, the system must:
  - abstain,
  - or return partial answer with clear limitations.

### 7.2 Evaluation Hooks (Spec Level)

- The spec requires:
  - a set of “golden questions” (e.g., “What was total revenue last month?”) with known answers.
  - periodic checks where the RAG Analyst is run against these golden questions and evaluated for:
    - correctness,
    - grounding,
    - citation quality.[web:11][web:122]

---

## 8. Deliverables from the Vibe-Coded Implementation

A vibe‑coded implementation of this spec is expected to produce:[web:120][web:122][web:125]

1. **Backend**:
   - FastAPI service exposing `/ask`, `/ingest`, `/eval` endpoints.
   - RAG retrieval and metric calculation modules.
   - local LLM client and optional cloud LLM client with routing logic.

2. **Frontend**:
   - Web UI for questions, filters, and answer visualizations.
   - Feedback controls and drill‑down views.

3. **Configuration**:
   - YAML/JSON spec for mapping client DB/CSV schemas into `sales`, `inventory`, `products` semantics.
   - Environment files for local vs hybrid (cloud) modes.

4. **Tests & evals**:
   - automated tests for key workflows and golden questions.
   - scripts for periodic evaluation and monitoring.

---

## 9. Open Design Slots (To Fill Later)

The spec intentionally leaves room for later refinement, including:

- Detailed metric definitions (e.g., exact margin formulas, discount handling).
- Specific forecasting models (naive vs advanced).
- The exact local model families (Qwen, Mistral, Llama) you’ll standardize on.

Those can be added as separate sections once you decide on final metric semantics and model choices.
