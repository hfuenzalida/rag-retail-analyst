# 9. Add Deployment and Preview Controls

we need to lock down how your suite moves from local development to preview, staging, and production, and what runtime controls can be changed safely after deploy. For AI systems, the important controls are not just infra; they also include model configs, prompts, routing rules, rollout percentages, fallbacks, and auditability.

Environments
1. Which environments do you want to formalize for this suite?

local only,

local + preview,

local + preview + staging + production,

or something else?

Formalized Environments: Implement the complete four-tier topology: local $\rightarrow$ preview $\rightarrow$ staging $\rightarrow$ production. This progression is essential for verifying how local model execution handles real network conditions before client-facing rollouts.

2. Should preview environments exist per pull request, with isolated URLs for reviewers, or do you prefer a shared staging environment only? Per-PR previews are commonly used to test app behavior against production-like infrastructure before merge.

Preview Scope: Utilize Shared Staging + Ephemeral Preview branches instead of fully dynamic, per-PR pipelines. Because your pipeline balances heavy local model infrastructure alongside database dependencies, fully dynamic per-PR preview environments can cause severe hardware utilization bottlenecks.

3. For preview environments, do you want them to include:

backend only,

frontend + backend,

or full stack including database and background jobs?

Deployment targets

Preview Stack Layout: Preview environments should run the Full Stack, excluding the heavy local LLM hardware services. The stack must deploy the Next.js frontend, FastAPI backend, and an isolated PostgreSQL/pgvector instance pre-loaded with mock data.

. Where do you want the suite deployed?

self-hosted VPS,

Docker on your own server,

Kubernetes,

Render,

Koyeb,

Northflank,

another provider?

5. Will local LLM components remain on your own hardware/self-hosted, while frontend/backend may deploy elsewhere, or do you want the entire stack deployable in one hosted environment?

Target Platforms & Hardware Splits: Adopt a Hybrid Sovereign Deployment model.

    Frontend/Backend API: Deploy inside isolated Docker containers on a highly controlled self-hosted VPS, a dedicated server, or isolated cloud environments.

    Local LLM Infrastructure: Keep local processing components (Ollama/vLLM runtimes) locked to your dedicated hardware nodes to ensure maximum data sovereignty. Connect your cloud-hosted API containers to these local clusters via encrypted, secure network overlays like Cloudflare Tunnels or WireGuard.

Deployment unit and packaging
6. What should be the primary deployment artifact?

Docker images,

docker-compose stacks,

Helm/Kubernetes manifests,

simple Git-based app deploys?

Primary Deployment Artifact: Standardize on immutable Docker Images managed via docker-compose stacks for localized client deployments, while structuring your configurations to easily port to Kubernetes manifests if an enterprise client demands orchestration scale later.

7. Do you want separate deployables for:

frontend,

backend API,

database,

vector store,

worker/background jobs,

local model services?

Service Separation Bounds: Split the system architecture into 5 isolated container targets to maximize resource allocation and scaling:

    frontend-ui: Next.js static asset server.

    backend-api: FastAPI application runner.

    postgres-db: Unified relational and vector (pgvector) store.

    worker-queue: Celery or n8n container handling heavy document ingestion pipelines.

    llm-inference: Local Ollama/vLLM runtime (isolated to GPU-enabled hardware nodes).

Preview controls
8. In preview environments, should the app use:

mock/sample datasets only,

sanitized test datasets,

or a production-like clone with masked data?

Dataset Seeding Strategy: Use Sanitized, masked test datasets in your preview and staging environments. Never expose raw corporate transactional text or unmasked client identifiers to non-production systems.

9. Should preview environments be allowed to call any cloud LLMs, or must they remain local/test-only to control spend and protect data?

Cloud LLM Spend Caps: Preview environments are permitted to contact cloud LLMs, but they must utilize tightly rate-limited, capped test API keys. This allows you to evaluate your hybrid local/cloud routing switches under realistic conditions without risking budget overruns.

10. Do you want preview deployments to have strict feature limits, for example:

no write actions,

no ingestion,

no admin controls,

no external email/webhook sending?

Strict Feature Restrictions: Enforce an absolute read-only boundary in preview systems. Hardcode environmental flags that completely disable write actions, pipeline data ingestion, administrative configurations alterations, and external communication webhooks.

Promotion flow
11. What should be the formal promotion path?

preview → production,

preview → staging → production,

local → staging → production,

or another sequence?

Promotion Path Execution: Execute the sequential path: local $\rightarrow$ preview (PR verification) $\rightarrow$ staging (pre-release baseline validation) $\rightarrow$ production (client node rollout).

12. What should be required before promotion from one environment to the next?

passing unit/integration tests,

offline eval thresholds,

smoke tests,

human approval,

performance checks,

security checks?

Runtime controls after deploy

Mandatory Promotional Gates: To move code to the next deployment tier, the build pipeline must satisfy 5 automated and manual validation blocks:Code Quality: 100% success across all pytest unit and integration test fixtures.AI Performance: Meet or exceed all Pydantic Evals golden question thresholds ($\ge$95% factual accuracy, $\ge$98% groundedness).System Smoke Test: Automated confirmation of API health and end-to-end routing.Data Integrity: Linting verification of database schemas and configuration files.Human Sign-Off: Explicit manual code-owner review and merge approval.

13. Which controls do you want to be runtime-configurable without redeploy?
Examples:

model/provider selection,

prompt version,

routing thresholds,

cloud enable/disable flags,

feature flags,

rollout percentages,

eval sampling rates.

Hot-Swappable Runtime Controls: These variables must be configurable on the fly via an administrative dashboard or dynamic runtime configuration files without needing a full server restart:

    Default model selections.

    Sensitivity classification routing parameters.

    Cloud provider feature toggles.

    Live evaluation sampling frequencies (e.g., dialing Logfire monitoring from 5% to 20%).

14. Which controls must always require redeploy or code review because they are too sensitive?
Examples:

RBAC logic,

secret handling,

schema changes,

core tool behavior,

financial metric formulas.

Feature flags and progressive delivery

Core Hard-Locked Parameters: Any alteration to these baseline parameters requires a full code review and redeployment:

    Role-Based Access Control (RBAC) permission logic.

    Secrets management schemas and database encryption keys.

    Database structures and indices.

    Core metric computation logic and financial formulas.

15. Do you want to formalize feature flags for this suite so deployment and release are separate? That is a common best practice for rolling out new AI behavior gradually and safely.

Feature Flag Formalization: Yes, decouple code deployment from operational feature releases by baking flag primitives into your codebase from day one.

16. If yes, which capabilities should start behind flags?

new prompts,

new model providers,

cloud routing,

chart generation,

recommendation engine,

ingestion workflows,

admin actions?

Early Flag Targets: Keep new system prompts, cloud routing parameters, and predictive recommendation algorithms completely behind feature flags.

17. How do you want rollouts to happen?

internal users only,

selected testers,

percentage rollout,

per-client rollout,

per-role rollout (manager vs analyst)? Progressive rollout with guardrail metrics is a common AI deployment pattern.

Targeted Release Strategy: Execute a structured, Role-Based Progressive Rollout matrix:

    Internal Developers: Full feature visibility inside staging.

    Client Sandbox Testers: Initial exposure to specialized feature slices.

    Production Analysts: Features go live for technical analyst roles first.

    Production Managers: General rollout to high-level summaries and dashboards once performance metrics stabilize.

Fallbacks and kill switches
18. What should happen if:

cloud provider fails,

local LLM becomes unavailable,

groundedness metrics drop,

latency spikes,

routing misbehaves?

18 & 20. Failure Recovery & Layered Fallbacks: Implement an automated, tiered fallback structure to guarantee system availability:

    Cloud LLM Failure: Automatically down-route the analytical query to your last-known-good local LLM engine.

    Local Hardware Overload: If VRAM utilization spikes or scheduling queues stall, return a graceful, pre-formatted UI notification alongside a structured error block.

    Groundedness Score Drops: If live evaluations detect a systemic drop in correctness, trigger a kill switch that reverts the active prompt version to the previous stable release.

19. Do you want explicit kill switches for:

cloud routing,

a specific provider,

a prompt version,

a feature flag,

automated recommendations?

Granular Kill Switches: Expose explicit kill switches inside your control panel for cloud routing mechanisms, specific remote API providers, newly modified prompt profiles, and automated recommendation engines.

20. What is the default fallback behavior?

revert to local-only,

revert to last-known-good prompt/model config,

disable the feature and return a safe error,

or some layered combination?

Preview and deployment observability

18 & 20. Failure Recovery & Layered Fallbacks: Implement an automated, tiered fallback structure to guarantee system availability:

    Cloud LLM Failure: Automatically down-route the analytical query to your last-known-good local LLM engine.

    Local Hardware Overload: If VRAM utilization spikes or scheduling queues stall, return a graceful, pre-formatted UI notification alongside a structured error block.

    Groundedness Score Drops: If live evaluations detect a systemic drop in correctness, trigger a kill switch that reverts the active prompt version to the previous stable release.

21. What metrics must be checked in preview/staging before promotion?

error rate,

latency,

groundedness,

abstention correctness,

citation quality,

cost per request,

cloud handoff rate?

Pre-Promotion Evaluation Metrics: Staging validation scripts must audit system performance across 4 critical metrics: Error rate ($\le$1%), response latency, factual accuracy scores, and the cloud handoff rate to prevent unpredicted token expenses.

22. Do you want shadow deployments for major model/prompt changes, where the new version runs alongside the current one without serving users yet? This is a recommended practice for AI changes that are hard to validate with only static tests.

Shadow Deployment Execution: Yes, support shadow deployments for high-impact model migrations. Route duplicates of live, non-sensitive queries to your experimental model pipeline in the background to analyze response quality and latency variants before routing user traffic to it.

Access control
23. Who should be able to access preview and staging?

only you,

internal reviewers,

client stakeholders,

password-protected public links,

SSO users only?

Non-Production Access Rules: Restrict preview and staging networks exclusively to authenticated internal team members and selected project owners via Single Sign-On (SSO) or robust, IP-whitelisted access tokens.

24. Should preview URLs expose:

all app routes,

only demo routes,

or role-limited slices of the product?

Preview Interface Exposure: Expose only dedicated demo routes and isolated data tables within non-production environments to prevent accidental leakage of real workflow frameworks.

Data and tenant boundaries
25. Since you’re planning a controlled, client-aware architecture, should deployments be:

single-tenant per client,

shared app with logical isolation,

or local per-client deployments first, shared later?

Multi-Tenancy Architecture Selection: Implement an Isolated Single-Tenant Node model per client cluster for your production instances. This completely isolates each client's data structures, vector databases, and log files into independent infrastructure boundaries, matching strict enterprise compliance needs.

26. In preview/staging, do you want a mandatory client_id isolation model enforced exactly like production, even if there is only one test tenant right now?

Mandatory Client Isolation: Enforce the exact same structural client_id logical validation filters inside your preview and staging environments that you use in production

Deployment governance in vibe coding
27. Should deployment config files be treated as Red Zone in the same way as routing, eval, and security logic?
Likely candidates:

infra/**

deployment manifests,

CI/CD configs,

env wiring,

release workflows.

Red Zone Infrastructure Constraints: All deployment blueprints, Kubernetes configurations, network routing parameters, and CI/CD parameters are strictly Red Zone assets.

28. Do you want Cursor/agents to:

only propose changes to deployment configs,

or be allowed to scaffold preview/deployment files that you review before apply?

Code Generator Tool Restrictions: Workspace automation assistants can only propose layout outlines or draft initial deployment stubs. They are completely blocked from executing automated terminal changes on production systems.

Deliverable shape
29. For section 9, do you want the final spec to focus mainly on:

environment model and release flow,

feature flags and runtime controls,

or a complete deployment-control blueprint covering both?

29 & 30. Standardized Architecture Layout

Organize your project configurations into a clean, modular repository layout to keep infrastructure parameters fully decoupled from application logic:
Plaintext

rag-retail-analyst/
  infra/
    docker-compose.local.yml      # Fully containerized local dev tree
    docker-compose.preview.yml    # Clean staging/preview app container stack
    deploy/
      production-node.yml         # Enterprise client deployment configuration
    flags/
      runtime-controls.yaml       # Dynamic hot-swappable configuration flags
  memory-bank/
    core/
      deployment-controls.md      # Master deployment blueprint document

30. do you also want this section to recommend a concrete file layout such as:

infra/docker-compose.local.yml

infra/docker-compose.preview.yml

infra/docker-compose.staging.yml

infra/deploy/

infra/flags/

memory-bank/core/deployment-controls.md?

