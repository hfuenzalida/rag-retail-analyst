# RAG Retail Analyst

**Sovereign AI data analyst** for retail inventory and sales: natural-language questions over structured metrics and document-backed context, with a FastAPI agent layer, PostgreSQL + pgvector, and a Next.js operator UI.

**Stack:** FastAPI · Pydantic AI agents · PostgreSQL · pgvector · Next.js  
**License:** [MIT](LICENSE)  
**Topics:** `rag` · `retail` · `fastapi` · `nextjs` · `postgresql` · `pydantic-ai`

**Status:** Phase 4 complete (analyst UI, filters, admin CSV ingestion). Phase 5 targets evaluator hardening and hybrid cloud routing.

---

## Overview

This project shows how to ship a **domain-specific analyst** without surrendering data to a black-box SaaS: schemas and goldens live in-repo (`memory-bank/`), retrieval and SQL tools are explicit, and Docker Compose provides a one-command local stack for partner demos.

---

## Query workflow

<p align="center">
  <img src="docs/workflows/analyst-query.svg" alt="User question through routing agent, RAG analyst, evaluator, and PostgreSQL data plane" width="880"/>
</p>

---

## Quick start

```bash
git clone https://github.com/hfuenzalida/rag-retail-analyst.git
cd rag-retail-analyst
cp infra/env.example infra/.env.local
docker compose -f infra/docker-compose.local.yml up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 (`/docs`, `/healthz`) |
| UI | http://localhost:3000 |

### Local development (without Docker)

```bash
cd backend && pip install -r requirements.txt && pytest app/tests -v
cd frontend && npm install && npm run dev
```

Seed demo data (Postgres required):

```bash
cd backend && python -m app.db.seed
```

---

## Architecture layers

| Layer | Responsibility |
|-------|----------------|
| Data | `sales`, `inventory`, `products`, `rag_documents` (pgvector) |
| RAG | Ingestion, embeddings, hybrid retrieval |
| Agents | Pydantic AI orchestration (routing + analyst + evaluator) |
| Routing | Sensitivity check, local vs cloud LLM |
| API | `/query`, `/ingest`, `/eval`, `/healthz` |
| UI | Next.js Q&A and admin flows |

Authoritative specs for contributors and coding agents:

- `memory-bank/core/product-spec.md`
- `memory-bank/core/architecture.md`
- `memory-bank/core/agent-surface.md`
- `memory-bank/core/implementation-plan.md`

See also `CLAUDE.md` for guardrails.

---

## Repository layout

```
backend/app/      api, agents, tools, db, models
frontend/src/     UI components and API client
infra/            Docker Compose, env templates
memory-bank/      Specs, golden questions, plans
docs/workflows/   SVG diagrams
```

---

## Testing

```bash
cd backend && pytest app/tests -v
cd frontend && npm test && npm run build
# Optional DB integration:
# RUN_DB_INTEGRATION=1 pytest app/tests/test_integration_db.py -v
```

---

## Security configuration

- Copy `infra/env.example` to `infra/.env.local`; never commit secrets.
- Treat admin CSV ingestion as a **trusted-operator** action in production.

---

## Related portfolio repositories

| Repository | Focus |
|------------|--------|
| [fhir-interop-hub](https://github.com/hfuenzalida/fhir-interop-hub) | Healthcare · FHIR |
| [security-suite-orchestrator](https://github.com/hfuenzalida/security-suite-orchestrator) | DevSecOps |
| [digital-brain](https://github.com/hfuenzalida/digital-brain) | Founder OS |
| [ig-video-to-text](https://github.com/hfuenzalida/ig-video-to-text) | Media ML |
| [ai-3-layer-coder](https://github.com/hfuenzalida/ai-3-layer-coder) | AI routing |