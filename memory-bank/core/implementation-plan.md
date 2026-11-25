# Implementation Plan

Fine-grained build steps. Agents work **one step at a time**.

---

## Phase 0 — Foundation ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 0.1 | Repo layout, Settings, Docker local stack | `pytest app/tests`, `/healthz` 200 |
| 0.2 | Memory-bank + Cursor rules | Rules reference core memory files |
| 0.3 | API stubs `/query`, `/ingest`, `/eval` | Integration test for query stub |

---

## Phase 1 — Data Layer ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 1.1 | Repository + seed data loader | Unit tests with test DB |
| 1.2 | `run_metric_query` for core metrics | Metric unit tests |
| 1.3 | `get_top_drivers` (group-by deltas) | Driver unit tests |
| 1.4 | RBAC on metric tools | Permission denial tests |

---

## Phase 2 — RAG Layer ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 2.1 | Document ingestion to pgvector | Integration test retrieval |
| 2.2 | `search_docs`, `get_schema_docs` | RAG tool unit tests |
| 2.3 | CSV ingest + mapping agent (propose-only) | Admin flow test |

---

## Phase 4 — Frontend MVP ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 4.1 | Full AnswerPanel (metrics, drivers, actions) | Component tests |
| 4.2 | Filters and mode toggle | API integration |
| 4.3 | Admin ingestion UI | Admin flow |

## Phase 3 — Agents & `/query` ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 3.1 | Routing / sensitivity agent | Routing unit tests |
| 3.2 | Local LLM client (Ollama) | Mock + optional live test |
| 3.3 | RAG Analyst agent wired to tools | E2E golden smoke (10) |
| 3.4 | Logfire instrumentation | Trace visible in Logfire |

---

## Phase 4 — Frontend MVP

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 4.1 | Full AnswerPanel (metrics, drivers, actions) | Manual + component tests |
| 4.2 | Filters and mode toggle | API integration |
| 4.3 | Admin ingestion UI | Admin role test |

---

## Phase 5 — Hybrid Cloud & Evals ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 5.1 | Evaluator agent + `/eval/run` | Golden eval report |
| 5.2 | Cloud routing with sanitization | Routing integration tests |
| 5.3 | Golden dataset 50–75 questions | CI eval gates |
| 5.4 | OIDC + JWT auth | Auth integration tests |

---

## Phase 6 — Environments & CI/CD ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 6.1 | Preview/staging compose files | Smoke in staging |
| 6.2 | Feature flags + runtime controls | Flag toggle test |
| 6.3 | Promotion pipeline gates | Full gate checklist |

---

## Phase 7 — Production Rollout ✅

| Step | Goal | Tests to Pass |
|------|------|---------------|
| 7.1 | Single-tenant production node | Pilot client live |
| 7.2 | Kill switches + fallbacks | Failure injection tests |
| 7.3 | Role-based progressive rollout | Rollout matrix verified |
