# RAG Retail Analyst

Sovereign AI RAG Data Analyst for retail inventory and sales analytics.

## Quick Start

```bash
# Copy env template (optional — compose has defaults)
cp infra/env.example infra/.env.local

# Start local stack (Postgres + backend + frontend)
docker compose -f infra/docker-compose.local.yml up --build

# Backend tests (local, without Docker)
cd backend
pip install -r requirements.txt
pytest app/tests -v

# Seed demo data (requires PostgreSQL running)
cd backend
python -m app.db.seed

# Optional DB integration tests
set RUN_DB_INTEGRATION=1
pytest app/tests/test_integration_db.py -v

# Frontend dev
cd frontend && npm install && npm run dev

# Frontend component tests
cd frontend && npm test

# Frontend production build
cd frontend && npm run build
```

- **API**: http://localhost:8000 — docs at `/docs`, health at `/healthz`
- **UI**: http://localhost:3000

## Project Layout

```
backend/          FastAPI + agents + tools
frontend/         Next.js UI
infra/            Docker compose, env templates
memory-bank/      Specs, implementation plan, golden questions
.cursor/rules/    Cursor guardrails
docs/             Original planning specs (RAG Data Analyst *.md)
```

## For AI Assistants

Read before backend changes:

- `memory-bank/core/product-spec.md`
- `memory-bank/core/agent-surface.md`
- `memory-bank/core/architecture.md`
- `memory-bank/core/implementation-plan.md`

See `CLAUDE.md` for full assistant rules.

## Status

**Phase 4 complete** — full analyst UI, filters, admin CSV ingestion.

Next: **Phase 5** — evaluator, golden eval CI, hybrid cloud routing.
