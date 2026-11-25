# Architecture

## Layers

1. **Data** — PostgreSQL (`sales`, `inventory`, `products`), pgvector (`rag_documents`)
2. **RAG** — ingestion, embeddings, hybrid retrieval (Phase 2)
3. **Agents** — Pydantic AI multi-agent orchestration (Phase 3+)
4. **Routing** — sensitivity check, local vs cloud LLM (Phase 3+)
5. **API** — FastAPI `/query`, `/ingest`, `/eval`, `/healthz`
6. **UI** — Next.js question/answer interface

## Directory Responsibilities

| Path | Role |
|------|------|
| `backend/app/api/` | HTTP endpoints only |
| `backend/app/agents/` | Pydantic AI agent definitions |
| `backend/app/tools/` | Pure tool functions (metrics, RAG, routing, eval) |
| `backend/app/core/` | Config, logging, routing helpers |
| `backend/app/db/` | Schema and repository |
| `backend/app/models/` | Pydantic request/response models |
| `frontend/src/` | UI components and API client |
| `infra/` | Docker compose, env templates |
| `memory-bank/` | Specs, plans, golden questions |

## Request Flow (target)

```
User → POST /query → Routing Agent → RAG Analyst Agent → (sampled) Evaluator → QueryResponse → UI
```

## Governance Zones

- **Red Zone**: `core/`, `agents/`, routing/eval tools, prompts, metric logic, infra deploy configs
- **Green Zone**: frontend presentation, docs, non-sensitive helpers
