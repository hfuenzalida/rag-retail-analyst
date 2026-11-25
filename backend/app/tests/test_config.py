"""Settings model tests."""

from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_env == "local"
    assert settings.app_name == "rag-retail-analyst"
    assert settings.enable_openai is False


def test_settings_env_prefix(monkeypatch):
    monkeypatch.setenv("APP_APP_ENV", "staging")
    monkeypatch.setenv("APP_ENABLE_OPENAI", "true")
    settings = Settings()
    assert settings.app_env == "staging"
    assert settings.enable_openai is True
