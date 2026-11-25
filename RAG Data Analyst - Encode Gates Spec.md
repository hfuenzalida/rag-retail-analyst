# 5. Encode Quality Gates: Tests, Evals, and Review Rules

_Based on your completed Encode Gates answers._[file:184]

---

## 1. Testing Layers (Code-Level Quality Gates)

You will enforce three primary test layers in the FastAPI + Pydantic AI backend:

1. **Unit Tests**
   - Target:
     - Pure Python functions and tools:
       - `metrics_tools.py` (e.g., `run_metric_query`)
       - `rag_tools.py`
       - `routing_tools.py` (e.g., `check_sensitivity`, routing decisions)
       - `eval_tools.py`.[file:184][web:176][web:181]
   - Goals:
     - Verify metric calculations, driver analysis, routing decisions, and sensitivity checks deterministically.
     - Fully mock DB and LLM calls so tests remain isolated from external services and run quickly.[file:184][web:176][web:179][web:181]

2. **Integration Tests**
   - Target:
     - HTTP endpoints: `/query`, `/ingest/csv`, `/eval/run`.
   - Goals:
     - Ensure the chain **request → dependency injection → tools → response models** works end-to-end.
     - Validate `ErrorInfo` behavior, status codes, and basic `QueryResponse` structure.[file:184][web:176][web:181]
   - Implementation:
     - Use FastAPI `TestClient` plus fixtures to spin up an app.
     - Override dependencies for DB/LLM with mocks or test doubles.[file:184][web:181]

3. **Smoke Tests**
   - Target:
     - Deployed environments (staging, prod).
   - Goals:
     - Run a small set of “canary” questions after each deploy.
     - Confirm routing (local vs cloud), secrets access, and `/healthz` endpoints behave correctly.[file:184]

All core test suites must pass before any agentic behavior changes are considered safe.

---

## 2. Offline Evals (Dataset-Based AI Evaluation)

You will use **Pydantic Evals** to systematically test agent behavior against curated datasets.[file:184][web:171][web:173][web:182]

### 2.1 Golden Question Datasets

- Stored in `memory-bank/eval/golden-questions.json`.
- Each item includes:
  - `id`
  - `client_id`
  - `question`
  - `filters`
  - expected metrics/dimensions and acceptable patterns.[file:154][file:184][web:171]

Golden question coverage:

- Initial scope: **50–75 cases**:
  - ~25 for sales performance,
  - ~25 for low-stock inventory risk,
  - ~15 for security/routing edge cases.[file:184]
- Distribution:
  - ~70% focused on numeric/filtering correctness.
  - ~30% on narrative quality and recommendation usefulness.[file:184]

### 2.2 Evaluator Types and Thresholds

Implement multiple evaluators with strict thresholds:[file:184][web:171][web:149]

- **Factual Accuracy / Metric Correctness**
  - Compares returned metrics to expected DB values within tight tolerance.
  - Threshold: **≥ 95%** pass rate across golden questions.[file:184]

- **Groundedness / Hallucination**
  - LLM-as-judge plus deterministic checks to ensure claims are supported by retrieved context.
  - Threshold: **≥ 98%** groundedness; near-zero tolerance for phantom stock, invented trends, or unsupported claims.[file:184][web:171][web:149]

- **Abstention Behavior**
  - Evaluates whether agent correctly abstains (“I do not have access to this information”) when data is missing or permissions block access.
  - Threshold: **100%** abstention correctness: no hallucinated approximate answers in absence of data.[file:184]

- **Format Validation**
  - Checks that `QueryResponse` respects schema and business rules:
    - non-empty `summary`,
    - valid `routing_decision`,
    - appropriate `metrics` and `citations` shape.[file:184][web:173]

Evaluator judge model:

- Use a **flagship cloud LLM** (higher quality than local analytic models) as the judge for semantic groundedness and subtle distortions.[file:184][web:171][web:149]

### 2.3 Eval Frequency and Scope

You adopt a **tiered eval strategy**:[file:184][web:172]

- **Per-PR (CI)**:
  - Run full unit + integration tests.
  - Run a compressed subset of golden questions (e.g., ~10 core smoke-test queries) with single-run evals.

- **Nightly / Pre-release**:
  - Run full golden dataset.
  - Use multi-run settings (e.g., `repeat=5`) to measure stability and stochastic variance for each evaluator.[file:184][web:171][web:172][web:182]

- **Offline regression gates**:
  - Builds fail if:
    - factual accuracy < 95%,
    - groundedness < 98%,
    - any abstention case fails,
    - or format validation fails for required fields.[file:184]

---

## 3. Online Evals and Live Monitoring (Logfire)

You will use **online evals via Logfire** to continuously monitor production traffic.[file:184][web:172][web:177][web:152]

### 3.1 Sampling Strategy

- **Lightweight structural checks**:
  - 100% of production calls.
  - Verify schema correctness, `QueryResponse` structure, basic groundedness heuristics (context presence). [file:184][web:177]

- **Expensive LLM-as-judge evaluations**:
  - ~**5%** of production calls sampled.
  - Evaluate:
    - factual accuracy,
    - citation quality,
    - narrative clarity and recommendation quality.[file:184][web:172]

Sampling balance keeps continuous quality insight without exploding cloud costs.

### 3.2 Automated Red-Flag Triggers

Online eval metrics feed **tripwires** that open issues and page humans:[file:184][web:172][web:177]

- **Groundedness drop**:
  - Rolling groundedness < **95%** over any 100-request window triggers a high-priority alert.

- **Citation breakdown**:
  - Citation accuracy < **90%** or > **5%** of data queries returned without matching DB context pointers triggers investigation.

- **Routing drift**:
  - Cloud handoffs (cloud LLM usage) surge by > **20%** within 24 hours, indicating prompt/config drift or routing bug.[file:184]

Alerts surface in Logfire dashboards and/or external monitoring (PagerDuty, etc.), and must be treated as blocking quality incidents.

---

## 4. Review Rules and Human-in-the-Loop QA

AI evals perform the first pass; humans guard **critical decisions**.[file:184][web:172][web:149][web:178]

### 4.1 Red vs Green Review Zones

- **Green Zone**:
  - UI components, simple presentation logic, basic utils.
  - AI-generated changes can be auto-merged after tests, with lightweight human review.[file:184][file:170][web:167]

- **Red Zone**:
  - routing and sensitivity logic,
  - RBAC/permissions,
  - financial/inventory computations,
  - secrets/config,
  - eval logic and golden dataset definitions.[file:184][file:170][web:164][web:167]

Red-zone rules:

- Any PR touching red-zone files requires:
  - full unit + integration tests success,
  - offline evals above thresholds,
  - explicit human review and approval.

### 4.2 Review Workflow

You adopt a **“Red Zone Gatekeeper” code-owner model**:[file:184]

- Green-zone changes:
  - can be approved by regular reviewers using standard PR flow.

- Red-zone changes:
  - must be approved by a core technical architect / quality owner.
  - Code-owner protection configured so PRs cannot merge without their sign-off.

This ensures prompts, routing, permissions, and eval logic evolve deliberately, not accidentally.

---

## 5. Quality Gates in CI/CD

Your CI/CD pipeline implements hard gates:

1. **Tests**
   - All pytest unit + integration suites must pass; any failure blocks merge/deploy.[file:184][web:176][web:181]

2. **Offline Evals**
   - Pydantic Evals run on golden questions (full or partial, depending on tier).
   - If scores fall below defined thresholds, pipeline fails.[file:184][web:171][web:172][web:173]

3. **Static Security & Config Checks**
   - Linting or custom scripts verify:
     - no hard-coded secrets,
     - correct use of `Settings`,
     - RBAC and routing guards in place.[file:170][web:161][web:168]

4. **Red-Zone File Protection**
   - Paths like `core/config.py`, `routing_tools.py`, `eval_tools.py`, prompt configs, and golden-questions files are codeowner-protected.[file:184]

Only when all gates are satisfied are images built and pushed to staging/prod.

---

## 6. Vibe Coding-Specific Quality Constraints

Because you’re using vibe coding, you will **encode quality constraints directly in memory-bank and rules files**.[file:184][web:148][web:167][web:164]

- `memory-bank/core/testing-strategy.md`:
  - documents required tests and evals per implementation step,
  - describes thresholds (95/98/100%) and red-flag triggers.[file:184]

- `.cursor/rules/` and `CLAUDE.md` / `GEMINI.md`:
  - instruct agents to:
    - never bypass or delete tests/evals,
    - always update/add tests when changing tools or agents,
    - keep red-zone changes minimal, well-documented, and aligned with data contracts.[file:184][web:148][web:167]

Agents are guided to **propose** new tests/evals alongside code changes, not just feature code.

---

## 7. Tool Correctness and Trace-Based Evals

For critical tools like `run_metric_query` and `get_top_drivers`, you will not rely solely on test coverage; you will build **deterministic evaluators** inside Pydantic Evals:[file:184][web:171][web:182]

- Evaluators inspect OpenTelemetry/Logfire traces:
  - extract arguments and SQL/metric operations executed by tools.
  - compare them against a known matrix of valid query structures and expected outputs.

This closes the loop between:

- what the agent *intended* to do (tool call),
- what the tools *actually* did (trace),
- and whether the end response is correct and grounded.

---

With these quality gates—tests, offline/online evals, and strict review rules—your RAG Data Analyst becomes:

- measurable and monitored,
- resistant to silent regressions or hallucination drift,
- and compatible with high-velocity vibe-coded development without sacrificing reliability.
