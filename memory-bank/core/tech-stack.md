# Tech Stack

## Backend

- **FastAPI** — async HTTP API
- **Pydantic AI** — typed agents and tools (Phase 3+)
- **PostgreSQL + pgvector** — relational data and vector store
- **Ollama / vLLM** — local LLM inference (Phase 3+)
- **Logfire** — observability and agent tracing

## Frontend

- **Next.js 14 + React + TypeScript**
- Chart library TBD (Plotly or Vega-Lite)

## Infrastructure

- **Docker Compose** — local, preview, staging
- **AWS Secrets Manager** — staging/production secrets
- Optional Kubernetes for enterprise clients

## Commands

```bash
# Local stack
docker compose -f infra/docker-compose.local.yml up

# Backend dev (without Docker)
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .

# Tests
cd backend && pytest app/tests -v

# Frontend dev
cd frontend && npm install && npm run dev
```

## Environment Variables

All config uses `APP_` prefix via Pydantic `Settings`. See `infra/env.example`.
