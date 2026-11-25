# Deployment Controls

## Environment Topology

`local` → `preview` → `staging` → `production`

## Promotion Gates (all required)

1. 100% pytest pass
2. Eval thresholds: ≥95% accuracy, ≥98% groundedness, 100% abstention
3. Smoke: `/healthz`, canary questions, routing verified
4. Schema/config lint
5. Human code-owner sign-off for Red Zone changes

## Container Services

- `frontend-ui`, `backend-api`, `postgres-db`, `worker-queue`, `llm-inference`

## Hot-Swappable (no redeploy)

- Model selection, sensitivity thresholds, cloud toggles, eval sampling rate

## Hard-Locked (redeploy + review)

- RBAC, secrets schemas, DB schema, metric formulas, core tool behavior

## Preview Rules

- Full stack minus GPU LLM; sanitized data; read-only; rate-limited cloud keys

See `infra/env.example` and `RAG Data Analyst - Deployment and Preview Questions.md` for full detail.
