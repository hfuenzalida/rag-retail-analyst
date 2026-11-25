# 3. Project Scaffolding and Long-Term Memory Files (Final Spec)

_Based on your completed scaffolding answers and preferences._[file:154]

---

## 1. Repository Structure

### 1.1 Top-Level Layout

Use a consistent, vibecoding-friendly layout:

```text
rag-retail-analyst/
  backend/
  frontend/
  infra/
  memory-bank/
  .cursor/
  README.md
  CLAUDE.md  # or GEMINI.md, depending on your main assistant
```

This gives agents and tools a predictable tree to work with, and keeps backend, frontend, infra, and long-term context physically separated.[file:154]

### 1.2 `backend/` – FastAPI + Pydantic AI + RAG

```text
backend/
  app/
    main.py
    api/
      query.py          # /query endpoint
      ingest.py         # admin ingestion endpoints
      eval.py           # /eval/run endpoint
    core/
      config.py         # settings, env loading
      logging.py        # Logfire observability wiring
      routing.py        # local vs cloud routing logic
    models/
      query_request.py  # Pydantic request models
      query_response.py # Pydantic response models
      metrics.py        # Metric, TimeSeries, etc.
      drivers.py        # Driver models
      errors.py         # ErrorInfo model
    agents/
      rag_analyst.py    # main Pydantic AI RAG Analyst agent
      evaluator.py      # evaluation agent
      ingestion_agent.py# optional later
    tools/
      metrics_tools.py  # run_metric_query, get_top_drivers
      rag_tools.py      # search_docs, get_schema_docs
      routing_tools.py  # check_sensitivity, route_to_cloud_llm
      eval_tools.py     # evaluate_answer_faithfulness, etc.
    db/
      schema.sql        # base tables & indexes for metrics + RAG
      repository.py     # data access functions
    tests/
      test_query_api.py
      test_metrics_tools.py
      test_rag_tools.py
      test_routing_tools.py
      test_eval_tools.py
```

You standardize on **FastAPI + Pydantic AI** as the agentic backend stack, with strict type models and tool modules providing a clear agent surface.[file:154][web:122][web:130][web:147]

### 1.3 `frontend/` – Next.js/React TypeScript UI

You opted to keep a **Next.js/React (TypeScript)** frontend from the start:

```text
frontend/
  src/
    pages/
      index.tsx         # main question and answer UI
      admin.tsx         # ingestion + configuration UI
    components/
      QuestionForm.tsx
      AnswerPanel.tsx
      MetricsTable.tsx
      DriversTable.tsx
      ActionsList.tsx
      ErrorBanner.tsx
      LoadingSpinner.tsx
    lib/
      apiClient.ts      # typed client for /query, /ingest, /eval
    styles/
      ...
  package.json
  tsconfig.json
  next.config.js
```

This supports rich tables, charts, and decision views, and is friendly to AI coding assistants that generate type-safe React components.[file:154][web:147][web:145][web:151]

### 1.4 `infra/` – Local & Hybrid Deployment

```text
infra/
  docker-compose.local.yml     # local-only stack (Postgres, local LLM, backend, frontend)
  docker-compose.hybrid.yml    # hybrid stack (local + cloud LLM)
  env.example                  # example env vars
  k8s/
    backend-deployment.yaml
    backend-service.yaml
    postgres-statefulset.yaml
    ...
```

You use Docker for reproducible dev/test, and keep room for Kubernetes manifests for future deployments. These files provide the substrate that both humans and agents can reason about for environment configuration.[file:154][web:147][web:152]

---

## 2. Memory-Bank Directory Structure

You will drive AI coding and orchestration via **Markdown + JSON memory files**, organized under `memory-bank/`.[file:154][web:146][web:148][web:151]

```text
memory-bank/
  core/
    product-spec.md
    tech-stack.md
    implementation-plan.md
    progress.md
    architecture.md
    agent-surface.md
    data-contracts.md
    testing-strategy.md
  domains/
    retail/
      metrics-spec.md
      drivers-spec.md
      use-cases.md
  eval/
    golden-questions.json
```

This modular layout keeps the **core engine** and domain-specific specs cleanly separated, anticipating future reuse for other industries.[file:154]

---

## 3. Core Memory Files (Contents and Roles)

### 3.1 `memory-bank/core/product-spec.md`

Purpose: High-level product description.

Suggested sections:

- **Overview**
  - Retail RAG Data Analyst for small businesses.
- **User Personas**
  - Managers, store owners, operations analysts.
- **Key Outcomes**
  - Explain revenue and inventory changes.
  - Identify drivers and stock-out risks.
  - Provide actionable recommendations.
- **Non-Functional Requirements**
  - Sovereign/local-first data handling.
  - Hybrid local/cloud LLM with strict sensitivity routing.
  - Latency and reliability expectations.

This file is the “business spec” for the agentic system.[file:154]

### 3.2 `memory-bank/core/tech-stack.md`

Purpose: Declare canonical stack and commands.

Include:

- **Backend**
  - FastAPI, Pydantic AI, PostgreSQL + pgvector, local LLM runtime (Ollama/vLLM), Logfire for observability.[file:154][web:122][web:147][web:140][web:152]
- **Frontend**
  - Next.js + React (TypeScript), chosen charting library.
- **Infra**
  - Docker, optional Kubernetes, secrets management.
- **Commands**
  - `poetry run uvicorn app.main:app --reload` (example).
  - `docker-compose -f infra/docker-compose.local.yml up`.
  - `pytest backend/app/tests`.

This is the reference doc that vibe coding tools read to understand your stack and how to run things.

### 3.3 `memory-bank/core/implementation-plan.md`

Purpose: Fine-grained, step-based build plan.

You explicitly prefer **highly fine-grained tasks** with clear definitions of done.[file:154]

Structure:

- For each step (e.g., “Step 4.1: Implement vector DB connection”):
  - **Goal**
  - **Inputs**
  - **Outputs**
  - **Tests to pass**
  - **Notes**

Example sections:

1. Repo & env setup.
2. `/query` endpoint + request/response models.
3. Metric tools + DB schema for `sales`, `inventory`, `products`.
4. RAG tools + Postgres pgvector wiring (broken into substeps).
5. Local LLM integration.
6. Routing + `check_sensitivity`.
7. Evaluator agent + `/eval/run`.
8. Frontend index page.
9. Frontend admin page.
10. Error and logging behavior.

Agents can be asked to work on a **single step at a time**, reducing scope and avoiding partial, messy implementations.[file:154][web:148][web:153]

### 3.4 `memory-bank/core/progress.md`

Purpose: Running log of completed steps.

Format:

- Date
- Step ID (e.g., `4.1`).
- Summary of work done.
- Links to PRs or commits.
- Open issues/TODOs.

This gives future you and any assistant a **timeline** of what’s already implemented and what’s pending.[file:154][web:146]

### 3.5 `memory-bank/core/architecture.md`

Purpose: Narrative architecture reference.

Include:

- **Layer diagram in prose** (data, RAG, agents, routing, UI).
- Per-directory explanations:
  - `backend/app/api` – public HTTP surface.
  - `backend/app/agents` – Pydantic AI agents.
  - `backend/app/tools` – pure functions invoked by agents.
  - `backend/app/db` – data access and schema.
- Explanation of hybrid local/cloud modes and where sensitivity is enforced.

Agents use this to respect file responsibility boundaries instead of collapsing logic into one place.[file:154]

### 3.6 `memory-bank/core/agent-surface.md`

Purpose: Document the **agentic surface spec**.

Include:

- Pydantic models for `QueryRequest` and `QueryResponse`.
- Tool signatures and expected behavior:
  - `run_metric_query`, `get_top_drivers`,
  - `search_docs`, `get_schema_docs`,
  - `check_sensitivity`, `route_to_cloud_llm`,
  - evaluator tools, ingestion endpoints, config tools.
- RBAC rules:
  - how `client_id` and `role` are passed and checked.

You explicitly prefer **signatures + behavioral constraints**, not pseudo-code, to avoid double maintenance.[file:154]

### 3.7 `memory-bank/core/data-contracts.md`

Purpose: Formalize data schemas.

Sections:

- `sales` table layout.
- `inventory` table layout.
- `products` table layout.
- CSV column naming conventions and mapping rules.
- Required vs optional fields.

This file becomes the single source of truth for data assumptions used by ingestion, metric tools, and tests.[file:154]

### 3.8 `memory-bank/core/testing-strategy.md`

Purpose: overall testing and evaluation plan.

Include:

- Unit testing strategy for tools.
- Integration tests for `/query` and routing.
- Load/performance testing guidelines.
- Reference to `memory-bank/eval/golden-questions.json`.
- Plan for running `/eval/run` as part of CI.

You intend to wire Logfire from day one to trace agent runs, context retrieval, and routing decisions.[file:154][web:122][web:147][web:152]

---

## 4. Domain-Specific Memory Files

Under `memory-bank/domains/retail/`:

### 4.1 `metrics-spec.md`

- Enumerate metrics (`total_revenue`, `units_sold`, `stock_out_rate`, etc.).
- Define formulas and constraints.
- Link metrics to tables and filters.

### 4.2 `drivers-spec.md`

- Describe how driver analysis is computed (e.g., contribution by category, store, SKU).
- Outline any modeling assumptions (group-by deltas, SHAP if added later).

### 4.3 `use-cases.md`

- Document key retail scenarios:
  - “Identify products with high margin but frequent stock-out.”
  - “Explain weekly revenue variance.”
  - “Flag upcoming stock-out risk.”

These domain files allow you to later add other domains while reusing the core architecture.

---

## 5. Evaluation Memory: `golden-questions.json`

You prefer to store golden questions in a **JSON file** for programmatic access.[file:154]

Path:

```text
memory-bank/eval/golden-questions.json
```

Structure example:

```json
[
  {
    "id": "retail-001",
    "client_id": "demo-retail",
    "question": "What was total net revenue last month?",
    "filters": {
      "date_range": { "start_date": "2026-05-01", "end_date": "2026-05-31" }
    },
    "expected": {
      "metric_name": "total_revenue",
      "value": 123456.78
    }
  },
  {
    "id": "retail-002",
    "question": "Which category contributed most to margin last quarter?",
    "expected": {
      "dimension": "category",
      "top": "Shoes"
    }
  }
]
```

Your `/eval/run` endpoint and test scripts load this JSON directly for evaluation runs, avoiding markdown parsing complexity.[file:154]

---

## 6. Vibe Coding / IDE-Specific Memory Files

### 6.1 `CLAUDE.md` / `GEMINI.md`

At repo root:

- Summarize:
  - project description,
  - tech stack and commands,
  - directory structure,
  - high-level rules for agents (no hard-coded secrets, respect RBAC, maintain schema isolation).[file:154][web:151]
- Link to core memory-bank files:
  - “Read `memory-bank/core/product-spec.md`, `tech-stack.md`, `agent-surface.md` before making changes.”

### 6.2 `.cursor/rules/` (if using Cursor)

```text
.cursor/
  rules/
    architecture.mdc
    stack.mdc
    style.mdc
    agents.mdc
```

- `architecture.mdc`: instructs Cursor not to merge modules and to respect the backend/frontend/infra separation.[file:154][web:146][web:148]
- `stack.mdc`: asserts FastAPI + Pydantic AI + Postgres + local LLM as the canonical backend stack.[file:154]
- `style.mdc`: code style rules (typing, docstrings, etc.).
- `agents.mdc`: rules for tool usage and safety (e.g., forbid exposing raw SQL tools to manager role).

These files act as long-term “guardrails” for AI assistants working on the repo.

---

## 7. How Agents Interact with the Memory Bank

Your intended workflow:[file:154][web:146][web:148]

1. Before working on a feature, the agent:
   - Reads `memory-bank/core/*` and relevant domain files.
   - Understands architecture, stack, and current progress.
2. You assign a **single implementation-plan step** (e.g., “Step 4.1: implement pgvector wiring”).
3. Agent generates code limited to that step, updates:
   - `progress.md` with what was done,
   - optionally adjusts `architecture.md` if new modules are added.
4. You run tests and inspect diffs.
5. Only after validation does the agent move to the next step.

This fine-grained, memory-driven workflow aligns with best practice for vibe coding and agentic engineering: constrained scope, observable behavior, and strong type contracts.[file:154][web:134][web:153]

---

## 8. Summary

With this scaffolding and memory-bank spec:

- The repo is **ready for FastAPI + Pydantic AI agents**, Next.js UI, and hybrid local/cloud RAG deployment.
- Long-term context is captured in Markdown and JSON files rather than ephemeral prompts.
- Vibe coding tools have clear, documented boundaries and tasks, reducing the chance of messy or unsafe code generation.
- You can now begin implementing the suite step-by-step, with agents using these files as the “source of truth” for behavior and architecture.
