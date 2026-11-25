# CLAUDE.md — RAG Retail Analyst

## Project

Sovereign hybrid RAG Data Analyst for retail inventory and sales. FastAPI backend, Next.js frontend, PostgreSQL + pgvector, optional local/cloud LLMs.

## Commands

```bash
docker compose -f infra/docker-compose.local.yml up --build
cd backend && pip install -r requirements.txt && pytest app/tests -v
cd frontend && npm install && npm run dev
```

## Structure

- `backend/app/api/` — HTTP endpoints
- `backend/app/agents/` — Pydantic AI agents
- `backend/app/tools/` — metric, RAG, routing, eval tools
- `backend/app/core/config.py` — Settings (APP_ prefix, SecretStr)
- `memory-bank/core/` — source of truth for specs and plan

## Rules for Agents

1. Read `memory-bank/core/agent-surface.md`, `architecture.md`, `testing-strategy.md`, `implementation-plan.md` before backend edits.
2. Work one implementation-plan step at a time; update `progress.md` when done.
3. Never hard-code secrets; use `Settings`.
4. Red Zone (propose-only): core, agents, routing, eval, metric logic, prompts, infra deploy.
5. Green Zone (higher autonomy): frontend UI, docs, helpers.
6. Always add/update tests when changing tools, agents, or API.
7. RBAC enforced at tool level; agents must not expose raw SQL or ingestion to managers.

## Current Phase

Phase 0 complete. Phase 1 next: repository, metric tools, seed data.
