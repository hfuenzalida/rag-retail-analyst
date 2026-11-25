"""Single-tenant pilot client validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from app.core.config import Settings, get_settings


class TenantAccessError(Exception):
    """Raised when a request violates tenant boundaries."""


@dataclass
class TenantConfig:
    client_id: str
    display_name: str
    environment: str
    allowed_roles: list[str]
    features: dict[str, bool]


_tenant_cache: dict[str, TenantConfig | None] = {}


def resolve_tenant_config_path(settings: Settings | None = None) -> Path | None:
    cfg = settings or get_settings()
    if cfg.tenant_config_path:
        return Path(cfg.tenant_config_path)
    default = Path(__file__).resolve().parents[3] / "infra" / "clients" / "pilot-retail.yaml"
    return default if default.exists() else None


def load_tenant_config(settings: Settings | None = None) -> TenantConfig | None:
    path = resolve_tenant_config_path(settings)
    if path is None or not path.exists():
        return None

    cache_key = str(path.resolve())
    if cache_key in _tenant_cache:
        return _tenant_cache[cache_key]

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tenant = TenantConfig(
        client_id=str(raw["client_id"]),
        display_name=str(raw.get("display_name", raw["client_id"])),
        environment=str(raw.get("environment", "production")),
        allowed_roles=list(raw.get("allowed_roles", ["manager", "analyst", "admin"])),
        features={k: bool(v) for k, v in (raw.get("features") or {}).items()},
    )
    _tenant_cache[cache_key] = tenant
    return tenant


def validate_tenant_access(client_id: str, role: str, settings: Settings | None = None) -> None:
    """Enforce single-tenant pilot binding in production."""
    cfg = settings or get_settings()
    if cfg.app_env != "production":
        return

    if cfg.pilot_client_id and client_id != cfg.pilot_client_id:
        raise TenantAccessError(
            f"Client '{client_id}' is not authorized on this production node "
            f"(bound to '{cfg.pilot_client_id}')."
        )

    tenant = load_tenant_config(cfg)
    if tenant is None:
        return

    if client_id != tenant.client_id:
        raise TenantAccessError(f"Client '{client_id}' is not registered for this tenant node.")

    if role not in tenant.allowed_roles:
        raise TenantAccessError(f"Role '{role}' is not enabled for tenant '{tenant.display_name}'.")
