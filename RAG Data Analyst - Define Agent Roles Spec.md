# 7. Define Agent Roles and Prompts for the Suite

This section defines the **agent roster, responsibilities, tool surfaces, orchestration pattern, and prompt strategy** for the RAG Data Analyst suite. The design follows Pydantic AI’s typed-agent model, structured outputs, and multi-agent patterns so that each role is narrow, testable, and governed by explicit boundaries rather than vague autonomy.[web:200][web:210][web:130]

The suite should not rely on a single “do everything” agent. Instead, it should use a small number of sharply-defined agents, each with restricted tools and explicit output contracts. That approach reduces prompt drift, improves observability, and fits the Red Zone / Green Zone governance model already established for routing, security, and quality gates.[file:184][file:199][web:208]

---

## 1. Agent Roster

The suite will use **five primary agent roles**:

1. **RAG Analyst Agent** – the main business-facing analytical agent.
2. **Evaluator Agent** – the quality-control and regression-scoring agent.
3. **Ingestion / Schema Mapping Agent** – the data onboarding and schema-alignment agent.
4. **Routing / Sensitivity Agent** – the security-aware routing and execution-boundary agent.
5. **Ops / Maintenance Agent** – the internal maintenance and observability support agent.[file:154][file:141][web:210]

This roster preserves a clean separation between:
- answering business questions,
- evaluating answer quality,
- ingesting data,
- deciding execution boundaries,
- and maintaining the system over time.[file:154][file:184]

---

## 2. Primary Agent: RAG Analyst Agent

### 2.1 Role Definition

The **RAG Analyst Agent** is the core user-facing intelligence layer. Its responsibilities are:

- interpret manager or analyst questions,
- identify the relevant metrics and dimensions,
- call approved tools such as:
  - `run_metric_query`,
  - `get_top_drivers`,
  - `search_docs`,
  - `get_schema_docs`,
  - `generate_chart_spec` (if applicable),
- synthesize a grounded answer into a strict `QueryResponse` structure.[file:141][file:154][web:200][web:202]

This agent must be **strictly retrieval-grounded and tool-grounded**. It should not invent missing data or improvise unsupported business claims. Any interpretation beyond retrieved metrics and RAG context must be clearly labeled as a hypothesis or recommendation rather than a fact.[file:184][web:203][web:209]

### 2.2 Allowed Tools

The RAG Analyst Agent may directly call:

- `run_metric_query`
- `get_top_drivers`
- `search_docs`
- `get_schema_docs`
- `generate_chart_spec` (frontend-oriented utility).[file:141]

It must **never** directly call:

- ingestion or schema-write tools,
- secret/config management tools,
- raw SQL execution in v1,
- threshold mutation tools,
- any runtime write-back operation that changes production state.[file:141][file:170][file:199]

### 2.3 System Prompt Pattern

The analyst prompt should frame the agent as a **Senior Retail Data Analyst / AI Business Intelligence Partner** with the following behavioral rules:

- answer only from available metrics, retrieved context, and tool outputs,
- never fabricate values, trends, or causal explanations,
- ask for clarification when filters are missing or ambiguous,
- distinguish between:
  - supported findings,
  - hypotheses,
  - and recommendations,
- output strict structured JSON aligned with `QueryResponse`.[file:141][web:203][web:209]

### 2.4 Output Contract

The RAG Analyst Agent always returns a validated response with fields such as:

- `summary`
- `metrics`
- `drivers`
- `recommendations`
- `citations`
- `confidence`
- `routing_decision`
- optional structured `error` block when needed.[file:141][file:154]

This preserves frontend reliability and fits the strict Pydantic-output requirement already chosen for the suite.[file:141][web:130][web:200]

---

## 3. Evaluator Agent

### 3.1 Role Definition

The **Evaluator Agent** is the suite’s quality judge. Its role is not to answer business questions, but to evaluate whether answers are:

- factually correct,
- grounded in evidence,
- properly abstaining when data is insufficient,
- structurally compliant with the response schema,
- and stable across prompt/model changes.[file:184][web:171][web:173]

This agent participates in:

- offline evals against golden questions,
- selected online evals over sampled production traffic,
- regression checks after prompt, routing, or tool changes.[file:184][web:172][web:177]

### 3.2 Allowed Tools

The Evaluator Agent may call tools such as:

- `evaluate_answer_faithfulness`
- `evaluate_answer_relevance`
- `evaluate_abstention_behavior`
- `load_golden_dataset`
- `compute_regression_report`
- optional helper to suggest new golden questions when gaps are found.[file:184]

It should not call operational business data tools like `run_metric_query` during normal evaluation flows unless the eval harness explicitly permits it for deterministic comparison.[file:184]

### 3.3 System Prompt Pattern

Its persona should be a **Strict QA Judge / Factuality Auditor**. The prompt should instruct it to:

- score, not rewrite,
- identify exact failure modes,
- avoid soft, vague judgments,
- be conservative when evidence is weak,
- return numeric and boolean outputs rather than essay-like prose.[file:184][web:171][web:173]

### 3.4 Output Contract

A typical evaluator output should resemble a strict structure such as:

- `factual_accuracy`
- `groundedness`
- `abstention_correct`
- `format_valid`
- `failure_modes`
- `notes`
- `recommended_action`.[file:184]

This makes the evaluator usable both in CI and live observability dashboards.[file:184][web:172][web:177]

---

## 4. Ingestion / Schema Mapping Agent

### 4.1 Role Definition

The **Ingestion / Schema Mapping Agent** supports onboarding new datasets into the suite. Its responsibilities are:

- inspect CSVs or sample tables,
- infer likely mappings to canonical fields,
- validate samples against `data-contracts.md`,
- flag ambiguous columns or risky assumptions,
- optionally generate migration or mapping suggestions for review.[file:141][file:154][web:208]

This agent is advisory-first, not autonomous.

### 4.2 Allowed Tools

It may call tools such as:

- `map_csv_to_schema`
- `preview_mapped_sample`
- `validate_dataset_against_contracts`
- `suggest_ingestion_config`
- optionally `generate_migration_stub`.[file:141][file:154]

It should **not** auto-apply schema changes or overwrite canonical mappings in v1. Human confirmation remains mandatory before saving mappings or applying ingestion logic.[file:141]

### 4.3 System Prompt Pattern

Its persona should be a **Retail Data Engineer / Schema Mapping Specialist**. Its prompt should instruct it to:

- prioritize precision over convenience,
- never guess ambiguous mappings silently,
- assign confidence scores,
- highlight uncertain columns explicitly,
- produce structured mapping recommendations for UI review.[file:141][web:208]

### 4.4 Output Contract

Expected outputs include:

- proposed field mapping table,
- confidence per mapped field,
- required human decisions,
- validation warnings,
- inferred missing required fields.[file:154]

This makes the ingestion workflow safe for admin-assisted onboarding.

---

## 5. Routing / Sensitivity Agent

### 5.1 Role Definition

The **Routing / Sensitivity Agent** is the security-aware execution-boundary role. Its function is to decide whether a request should be:

- `local_only`,
- `cloud_assist`,
- or `cloud_only`,

based on query sensitivity, permission context, and workload characteristics.[file:141][file:170][file:199]

It exists because the suite explicitly separates:
- local sovereignty-sensitive execution,
- sanitized cloud-assisted processing,
- and forbidden runtime mutation paths.[file:170][file:199]

### 5.2 Allowed Tools

This agent may call:

- `check_sensitivity`
- `route_to_cloud_llm`
- `log_routing_decision`
- optionally `estimate_cost_impact`
- optionally `summarize_routing_stats` for observability support.[file:141][file:170]

It must not:
- modify prompts,
- override RBAC,
- or mutate configuration values at runtime.[file:170][file:199]

### 5.3 System Prompt Pattern

Its persona should be a **Security-Aware Routing Advisor**. The prompt should instruct it to:

- prefer local execution when in doubt,
- apply a strict sensitivity rubric,
- route only sanitized payloads to cloud providers,
- log concise rationale for each routing decision,
- fail closed when the rules are unclear.[file:141][file:170][web:208]

### 5.4 Output Contract

A routing decision should return structured fields such as:

- `sensitivity_level`
- `routing_decision`
- `sanitization_required`
- `cloud_provider_allowed`
- `reasoning_summary`.[file:141][file:170]

This ensures observability and auditability for every non-trivial execution path.

---

## 6. Ops / Maintenance Agent

### 6.1 Role Definition

The **Ops / Maintenance Agent** is an internal service-support role. It helps with:

- triggering `/eval/run`,
- reading Logfire traces and surfacing anomalies,
- proposing updates to `progress.md`,
- suggesting refactors based on recurring tool or routing failures,
- assembling issue summaries or maintenance PR drafts.[file:154][file:184][file:199]

This agent supports development and system health, not business analysis.

### 6.2 Allowed Tools

It may call:

- `run_eval_suite`
- `read_observability_summary`
- `summarize_logfire_incidents`
- `draft_progress_update`
- `draft_refactor_issue`
- optional Git helpers for draft PR preparation.[file:154][file:184]

It should not directly merge code or update Red Zone architecture files automatically.[file:199]

### 6.3 System Prompt Pattern

Its persona should be an **AI Reliability Engineer / Maintenance Coordinator**. Its prompt should instruct it to:

- identify regressions,
- summarize operational risks cleanly,
- prefer issue / draft-PR generation over direct mutation,
- and maintain a structured operational memory trail.[file:184][file:199]

---

## 7. Multi-Agent Orchestration Pattern

The suite should use a **sequential, bounded orchestration flow** rather than free-form agent swarming.[web:210][web:200]

### 7.1 Main `/query` Flow

The default call graph should be:

1. **Routing / Sensitivity Agent**
   - checks sensitivity and determines execution mode.
2. **RAG Analyst Agent**
   - retrieves metrics/context, calls approved tools, generates `QueryResponse`.
3. **Evaluator Agent** (sampled or gated)
   - scores groundedness, accuracy, and abstention behavior for offline or selected live traffic.[file:141][file:184][file:170]

This preserves strong boundaries between:
- deciding where execution may happen,
- generating business answers,
- and evaluating answer quality.[file:170][file:184]

### 7.2 Ingestion Flow

For `/ingest/csv` or related admin flows:

1. Ingestion / Schema Mapping Agent reviews sample rows.
2. Human confirms mappings.
3. Backend ingestion pipeline applies validated mapping.
4. Ops / Maintenance Agent may log the ingestion result or propose follow-up fixes.[file:141][file:154]

### 7.3 Escalation Rules

If the Evaluator Agent detects low groundedness or structural invalidity:

- it may trigger a re-run with stricter prompts in controlled environments,
- or raise an issue / red flag for human review in production contexts.[file:184][web:172]

It should not silently rewrite analyst answers in the same user-facing call path.

---

## 8. Prompt Governance and Storage

Prompts should be treated as **versioned configuration artifacts**, not hidden strings inside Python files.[file:141][file:154][file:199][web:209]

### 8.1 Storage Model

Prompt and tool descriptions should live in versioned config files under a structure such as:

- `memory-bank/agents/rag-analyst.md`
- `memory-bank/agents/evaluator.md`
- `memory-bank/agents/ingestion-agent.md`
- `memory-bank/agents/routing-agent.md`
- `memory-bank/agents/ops-agent.md`.[file:154]

Core Python functions still define executable tool logic, but prompt text, role boundaries, and behavioral rules remain editable as controlled config.[file:141][web:132]

### 8.2 Prompt Sensitivity Zones

Prompt files follow the same governance model as the codebase:

- **Red Zone prompts**:
  - RAG Analyst
  - Evaluator
  - Routing / Sensitivity.[file:184][file:170][file:199]

- **Green Zone prompts**:
  - simple documentation assistants,
  - low-risk UI helper prompts,
  - superficial formatting helpers.[file:199]

Red Zone prompt changes require tests, evals, and human approval before merge.[file:184][file:199]

---

## 9. Human–Agent Interaction Rules

The suite should standardize when agents ask clarifying questions and how they communicate uncertainty.[web:203][web:209]

### 9.1 Clarification Behavior

The RAG Analyst Agent should ask clarifying questions when:

- the metric is underspecified,
- the time window is ambiguous,
- required filters such as store, category, or SKU are missing,
- multiple valid interpretations would materially change the answer.[file:141]

A standard clarification template should be used, such as:

- “This can be answered more precisely if you specify the time window.”
- “There are multiple possible category scopes; choose one for a grounded answer.”[file:141]

### 9.2 Abstention Pattern

When data is missing or permission scope blocks access, agents must abstain cleanly using a structured response rather than approximate or hallucinated answers.[file:184] This aligns with the previously defined 100% abstention-correctness requirement for quality gates.[file:184]

---

## 10. Canonical Prompt Design Principles

Across all agents, prompt design should follow these non-negotiable rules:

- **Narrow role definition** – each agent solves one class of problem only.[web:210][web:200]
- **Strict tool boundary** – only approved functions are callable.[file:141]
- **Typed outputs** – Pydantic-validated structures are mandatory.[web:130][web:200]
- **Groundedness first** – use tool outputs and retrieved evidence before narrative synthesis.[file:184][web:203]
- **No hidden mutations** – agents recommend changes; humans approve runtime-affecting mutations.[file:199][file:170]
- **Versioned prompts** – prompt evolution is governed like code.[file:154][file:199]
- **Eval-linked prompt changes** – any prompt change to Red Zone agents must trigger tests and offline evals before merge.[file:184]

---

## 11. Recommended Initial Prompt Set

For v1, the suite should ship with these concrete prompt identities:

| Agent | Recommended identity | Output style | Governance |
|------|----------------------|-------------|------------|
| RAG Analyst | Senior Retail Data Analyst / AI BI Partner | Strict `QueryResponse` JSON | Red Zone [file:141][file:199] |
| Evaluator | Strict QA Judge / Factuality Auditor | Numeric/boolean eval report | Red Zone [file:184] |
| Ingestion / Schema Agent | Retail Data Engineer / Schema Mapping Specialist | Mapping table + confidence + warnings | Yellow/Controlled admin zone [file:141][file:154] |
| Routing / Sensitivity | Security-Aware Routing Advisor | Routing decision object + rationale | Red Zone [file:170][file:199] |
| Ops / Maintenance | AI Reliability Engineer / Maintenance Coordinator | Issue summaries, eval summaries, draft PR notes | Green-to-Yellow, depending on file touched [file:184][file:199] |

---

With these definitions, the suite gains a prompt architecture that is:

- **modular** enough for Pydantic AI multi-agent orchestration,
- **safe** enough for hybrid local/cloud execution,
- **auditable** enough for quality-gated production use,
- and **vibe-codeable** because prompts, tool surfaces, and boundaries are all explicit, versioned, and testable.[web:200][web:210][file:154][file:199]