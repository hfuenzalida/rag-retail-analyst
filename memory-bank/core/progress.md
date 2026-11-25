# Progress Log

## 2026-06-30 — Phase 7 Complete

| Step | Summary |
|------|---------|
| 7.1 | `docker-compose.production.yml`, pilot tenant config, `/healthz/ready`, single-tenant validation |
| 7.2 | Tiered LLM fallbacks (cloud→local→draft), extended kill switches, failure injection script |
| 7.3 | Role-based rollout matrix in runtime controls; gating for drivers, cloud, deep-dive, recommendations |

### Production go-live

```bash
cd infra
cp env.production.example .env.production   # set secrets
docker compose -f docker-compose.production.yml --profile init up seed-demo
docker compose -f docker-compose.production.yml up -d
```

## 2026-06-30 — Phase 6 Complete

| Step | Summary |
|------|---------|
| 6.1 | `docker-compose.preview.yml` + `docker-compose.staging.yml` with env templates |
| 6.2 | Runtime controls YAML wired to routing, recommendations, ingest guards; `/controls/runtime` API |
| 6.3 | Promotion gates (`run_promotion_gates.py`), smoke/lint scripts, GitHub Actions CI workflow |

### Open Issues

- Phase 7: production rollout, kill-switch drills, progressive rollout matrix
- Eval CI requires Postgres (seeded in GitHub Actions gates job)

## 2026-06-30 — Phase 5 Complete

| Step | Summary |
|------|---------|
| 5.1 | Evaluator agent + `POST /eval/run` with golden-question scoring |
| 5.2 | Cloud LLM client with PII sanitization; cloud polish path in query pipeline |
| 5.3 | 50+ golden cases (programmatic expansion + JSON base); CI script `infra/scripts/run_eval_ci.py` |
| 5.4 | JWT auth (`POST /auth/token`), Bearer + dev header fallback; admin guard on eval/ingest |

### Open Issues

- Phase 6: staging compose, feature flags, promotion gates
- Production OIDC provider wiring (issuer URL configured but not integrated)

## 2026-06-30 — Phase 4 Complete

| Step | Summary |
|------|---------|
| 4.1 | AnswerPanel with MetricsTable, DriversTable, ActionsList, CitationsList, FeedbackControls |
| 4.2 | QuestionForm filters (dates, store, category, SKU), mode/detail/role toggles |
| 4.3 | Admin page: CSV upload, mapping review, confirm ingest |

### Open Issues

- Phase 5: evaluator agent, `/eval/run`, OIDC auth

## 2026-06-30 — Phase 3 Complete

| Step | Summary |
|------|---------|
| 3.1 | Routing/sensitivity agent: `check_sensitivity`, `resolve_routing_decision`, routing YAML |
| 3.2 | Local LLM client (Ollama-compatible) with optional summary polish |
| 3.3 | Query pipeline + RAG analyst wired to `/query`; 10 golden smoke tests |
| 3.4 | Logfire spans on query pipeline and tool calls |

### Open Issues

- Phase 4: full frontend AnswerPanel with metrics, drivers, actions
- Phase 5: evaluator agent and `/eval/run`

## 2026-06-30 — Phase 2 Complete

| Step | Summary |
|------|---------|
| 2.1 | pgvector document ingestion, chunking, deterministic/Ollama embeddings, hybrid search |
| 2.2 | `search_docs`, `get_schema_docs` in `rag_tools.py`; schema docs seeded with demo data |
| 2.3 | CSV mapping agent (rule-based), `/ingest/csv/map`, `/ingest/csv/confirm`, `/ingest/documents` |

### Open Issues

- Phase 3: wire RAG + metric tools into RAG Analyst agent and local LLM

## 2026-06-30 — Phase 1 Complete

| Step | Summary |
|------|---------|
| 1.1 | Repository layer, connection pool, demo-retail seed loader (`python -m app.db.seed`) |
| 1.2 | `run_metric_query` for total_revenue, units_sold, stock_out_rate, gross_margin_pct |
| 1.3 | `get_top_drivers` with group-by period deltas (category, store_id, sku, channel) |
| 1.4 | RBAC: managers blocked from gross_margin_pct; role checks on all metric tools |

### Open Issues

- Phase 2: RAG retrieval and document ingestion
- Wire metric tools into RAG Analyst agent (Phase 3)

## 2026-06-30 — Phase 0 Complete

| Step | Summary |
|------|---------|
| 0.1 | Scaffolded repo: backend (FastAPI), frontend (Next.js), infra (docker-compose.local.yml), Settings model |
| 0.2 | Created memory-bank core files and `.cursor/rules/` |
| 0.3 | API stubs: `/query`, `/ingest/*`, `/eval/run`, `/healthz`; pytest suite |

### Open Issues

- Phase 1: implement metric tools and repository
- Choose chart library for `generate_chart_spec`
- Define exact margin formulas in `metrics-spec.md`
