"""Single-tenant production validation tests."""

import pytest

from app.core.config import Settings
from app.core.tenant import TenantAccessError, load_tenant_config, validate_tenant_access


def test_load_pilot_tenant_config():
    tenant = load_tenant_config(Settings())
    assert tenant is not None
    assert tenant.client_id == "demo-retail"
    assert "manager" in tenant.allowed_roles


def test_production_rejects_wrong_client(monkeypatch):
    monkeypatch.setenv("APP_APP_ENV", "production")
    monkeypatch.setenv("APP_PILOT_CLIENT_ID", "demo-retail")
    from app.core.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(TenantAccessError):
        validate_tenant_access("other-client", "manager")
    get_settings.cache_clear()


def test_non_production_allows_any_client():
    validate_tenant_access("any-client", "manager")
