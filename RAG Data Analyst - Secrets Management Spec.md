# 4. Secrets Management and Environment Model for the Retail RAG Data Analyst

_Based on your completed secrets-management answers and preferences._[file:170]

---

## 1. Environment Strategy

### 1.1 Canonical Environments

You will use three environments:

- `local` – developer laptops / internal test servers.
- `staging` – pre‑production, full stack with test data.
- `production` – client-facing deployments (local or cloud).

Each environment has:

- its own **environment variables** (per container/process),
- its own **secrets source**:
  - file-based (`.env.local`) for `local`,
  - **AWS Secrets Manager** for `staging` and `production`, with later ability to swap to HashiCorp Vault or Infisical if sovereignty requirements arise.[file:170][web:158][web:168]
- explicit `APP_ENV` flag: `local`, `staging`, or `prod`.

### 1.2 Configuration vs Secrets

- **Configuration (non-sensitive)**:
  - `APP_ENV`, `APP_LOG_LEVEL`, `APP_BASE_URL`, feature flags (e.g., `APP_ENABLE_OPENAI`).
  - Supplied via `.env.local` for dev, or CI/CD‑injected env vars for staging/prod.[file:170][web:155][web:162]

- **Secrets (sensitive)**:
  - DB credentials, local LLM endpoints where appropriate, cloud LLM API keys, Logfire token, JWT signing secrets.
  - Stored in:
    - git‑ignored `.env.local` only for local dev,
    - AWS Secrets Manager for staging/prod, fetched at runtime via IAM roles.[file:170][web:158][web:161][web:168]

Agents are instructed to **never hard‑code secrets** and to always access configuration via the unified `Settings` model.[file:170][web:161][web:162][web:168]

---

## 2. FastAPI + Pydantic Settings Model

### 2.1 `Settings` Class

In `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "rag-retail-analyst"

    # Database
    db_url: SecretStr

    # Local LLM endpoints
    local_llm_chat_url: str | None = None
    local_llm_embeddings_url: str | None = None

    # Cloud LLM providers
    enable_openai: bool = False
    enable_anthropic: bool = False
    enable_gemini: bool = False

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None

    # Auth
    auth_jwt_secret: SecretStr
    oidc_client_id: str | None = None
    oidc_client_secret: SecretStr | None = None
    oidc_issuer_url: str | None = None

    # Observability (Logfire)
    logfire_token: SecretStr | None = None
    logfire_environment: str | None = None

    class Config:
        env_file = ".env"  # overridden per environment in local dev
        env_prefix = "APP_"
```

Key elements that match your preferences:

- Separate `local_llm_chat_url` and `local_llm_embeddings_url` so chat and embedding workloads can be scaled and optimized independently.[file:170]
- Feature flags `enable_*` for each cloud provider to act as guardrails; if a client disables a provider or lacks keys, routing gracefully falls back to local models or alternatives.[file:170]
- `SecretStr` for all sensitive values so they’re not printed in logs.[file:170][web:156]
- OIDC (Google/Microsoft/OAuth2) integrated via `oidc_*` fields, plus an **internal JWT** secret used for short‑lived tokens inside the agent execution layer.[file:170]

### 2.2 Settings Loading

In `backend/app/app/main.py`:

```python
from .core.config import Settings

settings = Settings()  # reads env vars or .env as appropriate
```

Using FastAPI dependencies, routes and tools receive `settings` rather than referencing globals.[file:170][web:155][web:162]

---

## 3. Secrets Sources and Patterns

### 3.1 Local Development (`APP_ENV=local`)

- Secrets kept in `infra/.env.local` (git‑ignored):
  - `APP_DB_URL=...`
  - `APP_LOCAL_LLM_CHAT_URL=http://localhost:8001/v1`
  - `APP_LOCAL_LLM_EMBEDDINGS_URL=http://localhost:8002/v1`
  - `APP_AUTH_JWT_SECRET=dev-secret`
  - Optional dev cloud keys: `APP_OPENAI_API_KEY`, etc.[file:170]
- `infra/docker-compose.local.yml` uses `env_file: infra/.env.local` for backend and local LLM services.

### 3.2 Staging & Production (`APP_ENV=staging` / `APP_ENV=prod`)

- **AWS Secrets Manager** is the canonical secrets backend:
  - Stores DB passwords, cloud API keys, JWT secret, Logfire token, OIDC client secrets.[file:170][web:158][web:168]
- FastAPI retrieves secrets at startup via IAM roles:
  - A small helper in `config.py` abstracts provider access so you can later swap to Vault/Infisical without touching agents.[file:170]
- No `.env` files with production secrets are written by CI/CD; secrets are pulled from the manager directly into process memory.[file:170][web:161][web:168]

You’ll enforce a **quarterly (90‑day) rotation** schedule for keys and credentials, supported by a script (e.g., `infra/secrets/rotate.sh`) that:

- updates secrets in AWS Secrets Manager,
- validates connectivity in staging,
- only then promotes the new secrets to production.[file:170]

---

## 4. Environment-Specific Behavior

### 4.1 Local

- Logging: verbose, console output.
- Routing:
  - prefer local LLM endpoints; allow cloud LLM calls for dev using test keys.
- Security:
  - simplified auth but still tokenized,
  - no hard-coded secrets anywhere.

### 4.2 Staging

- Same RBAC, routing, and sensitivity policies as production.
- Uses test datasets and potentially smaller or cheaper LLM models/quotas.
- All secret rotation and observability changes are tested here before prod.[file:170]

### 4.3 Production

- Strict RBAC based on `role` and `client_id`.
- All secrets resolved from AWS Secrets Manager.
- Routing:
  - `check_sensitivity` must run before any potential cloud call; `high` sensitivity forces `local_only`.
- Networking:
  - Mandatory **Zero-Trust proxy layer** (Cloudflare Tunnel or Nginx reverse proxy):
    - app never exposes raw port 80/443 to the public internet.
    - inbound traffic terminates at proxy, then tunnels to backend.[file:170][web:157][web:161][web:162][web:164]

---

## 5. Local vs Cloud LLM Endpoints

You decided to split local LLM endpoints into **chat** and **embeddings** services:

- `APP_LOCAL_LLM_CHAT_URL=http://llm-chat:8001/v1`
- `APP_LOCAL_LLM_EMBEDDINGS_URL=http://llm-embed:8002/v1`[file:170]

Rationale:

- Avoid scheduling bottlenecks and VRAM collisions by running generative and embedding models on separate runtimes (Ollama/vLLM).
- Allow independent scaling and hardware tuning (e.g., more GPU reserved for embeddings in heavy RAG workloads).[file:170][web:96][web:105]

Cloud LLM integration:

- Providers: OpenAI, Anthropic, Gemini.
- Each has:
  - API key,
  - URL base (if needed),
  - `enable_*` flag (e.g., `APP_ENABLE_ANTHROPIC=true`).
- Routing logic:
  - checks flags and presence of keys before even attempting cloud calls,
  - gracefully falls back to local LLM when provider disabled or missing.[file:170]

---

## 6. Auth Model and Secrets

Authentication is **hybrid**:

- External OIDC/OAuth2 (Google/Microsoft Workspace, etc.) for user login and identity.[file:170]
- Internal JWT for agent-layer security context:
  - `APP_AUTH_JWT_SECRET` used to sign short-lived tokens.
  - Tokens carry `client_id` and `role`, used by backend tools to enforce RBAC before running powerful operations.[file:170][web:159][web:165]

OIDC client secrets and issuers are stored in AWS Secrets Manager; the JWT secret is also managed there and rotated like other secrets.

---

## 7. Logfire Observability Integration

Logfire is wired from day one:

- Env vars:
  - `LOGFIRE_ENVIRONMENT=local|staging|prod`
  - `LOGFIRE_TOKEN=...` (from Secrets Manager).[file:170][web:160][web:152]
- `backend/app/core/logging.py`:
  - `logfire.configure()` using env or `pyproject.toml`.[web:160][web:163][web:166]
  - `logfire.instrument_pydantic_ai()` to trace agent runs and evaluations.[web:163][web:169]

You will use Logfire to:

- visualize which tools each agent calls,
- inspect routing decisions (local vs cloud),
- analyze `/eval/run` results over time.[file:170]

---

## 8. Security Guardrails for Vibe Coding

You explicitly want strong guardrails in **rules files** for Claude/Cursor/Gemini and similar environments.[file:170][web:161][web:164][web:167]

### 8.1 Rule Content (CLAUDE.md / GEMINI.md / `.cursor/rules/*.mdc`)

Rules include:

- Prohibitions:
  - no hard-coded API keys or passwords in code,
  - no reading `.env.local` contents from agents,
  - no unsafe `eval()` or reflection,
  - no non-parameterized SQL.[file:170][web:161][web:168]
- Requirements:
  - all config access via `Settings` class,
  - all secrets loaded from env or AWS Secrets Manager abstraction,
  - RBAC enforced at tool level before the LLM gets involved.[file:170][web:164]

### 8.2 Red vs Green Zones

You separate:

- **Green Zone**:
  - frontend components,
  - pure presentation,
  - small helpers.
  - AI agents can generate code more freely here.[file:170][web:167]

- **Red Zone**:
  - auth,
  - secrets,
  - routing,
  - data sanitization,
  - financial or sensitive logic.
  - Agents may propose changes, but you review diffs before merge.[file:170][web:164][web:167]

This aligns enterprise vibe coding guidance: high-velocity generation with layered governance.

---

## 9. Error and Configuration Safety

To avoid inconsistent deployments:

- Startup configuration:
  - `Settings` validation fails fast if required env vars/secrets are missing, with clear error messages.
- Defaults:
  - Only non-sensitive config has defaults; secrets must be provided explicitly.[file:170]
- Structured error model:
  - `ErrorInfo` (`code`, `message`, `retry_hint`) is used in API responses to guide users to self-correct prompts or configuration, without leaking internal details.[file:141][file:154]

---

## 10. CI/CD Integration

You chose to **avoid generating `.env` files with real secrets** during CI/CD:

- CI/CD pipelines:
  - inject non-sensitive env vars (e.g., `APP_ENV=staging`, `APP_LOG_LEVEL=info`),
  - assign IAM roles for Secrets Manager access.[file:170]
- Apps fetch secrets at runtime from Secrets Manager into memory; no secret-containing files are written to disk.[file:170][web:161][web:168]

This reduces risk of secret leakage through build logs, runner artifacts, and cached deployments.

---

With this secrets and environment model, your RAG Data Analyst suite is:

- secure and compliant for hybrid local/cloud deployments,
- ready for multi-tenant expansion,
- friendly to vibe coding tools without ever exposing raw keys,
- and instrumented for observability and evaluation from day one.
