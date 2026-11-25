# Testing Strategy

## Layers

1. **Unit tests** — tools and pure functions; mock DB/LLM
2. **Integration tests** — `/query`, `/ingest`, `/eval` via FastAPI TestClient
3. **Smoke tests** — deployed env canary questions + `/healthz`

## Offline Evals (Phase 5+)

- Dataset: `memory-bank/eval/golden-questions.json`
- Thresholds:
  - Factual accuracy ≥ 95%
  - Groundedness ≥ 98%
  - Abstention correctness 100%
- Per-PR: compressed golden subset (~10 questions)
- Nightly: full set with `repeat=5`

## Online Evals (Logfire)

- 100% structural validation on production traffic
- ~5% LLM-as-judge sampling

## Red-Flag Triggers

- Groundedness < 95% over 100-request window
- Citation accuracy < 90%
- Cloud handoff surge > 20% in 24h

## CI Gates

- All pytest pass
- Offline eval thresholds met (when implemented)
- No hard-coded secrets
- Red Zone changes require code-owner review
