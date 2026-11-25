# Role-Based Progressive Rollout Matrix

Progressive delivery stages for the Sovereign RAG Retail Analyst pilot.

## Stages

| Stage | Roles | Purpose |
|-------|-------|---------|
| Internal | `admin` | Full controls, eval, ingest, runtime flag management |
| Analysts | `analyst` | Deep-dive, drivers, cloud routing (when enabled) |
| Managers | `manager` | Summary metrics and recommendations only |

## Feature Matrix (defaults)

| Feature | Admin | Analyst | Manager |
|---------|-------|---------|---------|
| `cloud_routing` | yes | yes | no |
| `new_prompts` | yes | yes | no |
| `recommendation_engine` | yes | yes | yes |
| `deep_dive_mode` | yes | yes | no |
| `driver_analysis` | yes | yes | no |

Configured in `infra/flags/runtime-controls.yaml` under `rollout:`.

## Kill Switches

Instantly disable without redeploy:

- `cloud_routing` — force all queries to local-only polish
- `local_llm` — skip LLM polish, return grounded draft
- `openai_provider` — block OpenAI even if cloud routing enabled
- `new_prompts` — revert to stable prompt
- `automated_recommendations` — suppress action recommendations

## Fallback Chain

```
cloud_assist polish → local LLM polish → grounded draft summary
```

Cloud failure automatically down-routes to local. Local failure returns the deterministic metric summary.

## API

- `GET /controls/rollout` — view matrix (admin)
- `PATCH /controls/runtime` — toggle flags/kill switches (admin)
