"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Unified settings model. All secrets use SecretStr and APP_ env prefix."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_name: str = "rag-retail-analyst"
    app_log_level: str = "info"
    app_base_url: str = "http://localhost:3000"

    # Database
    db_url: SecretStr = SecretStr("postgresql://postgres:postgres@localhost:5432/rag_analyst")

    # Local LLM endpoints (split chat vs embeddings)
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
    auth_jwt_secret: SecretStr = SecretStr("dev-secret-change-in-production")
    oidc_client_id: str | None = None
    oidc_client_secret: SecretStr | None = None
    oidc_issuer_url: str | None = None

    # Observability
    logfire_token: SecretStr | None = None
    logfire_environment: str | None = None
    logfire_ignore_no_config: bool = True

    # Eval thresholds
    eval_min_factual_accuracy: float = 0.95
    eval_min_groundedness: float = 0.98
    default_cloud_provider: str = "openai"

    # Environment controls
    read_only: bool = False
    enable_ingest: bool = True
    runtime_controls_path: str | None = None

    # Production single-tenant
    pilot_client_id: str | None = None
    tenant_config_path: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
