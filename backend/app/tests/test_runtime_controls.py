"""Runtime controls unit tests."""

from pathlib import Path

import yaml

from app.core.runtime_controls import (
    apply_runtime_controls_update,
    cloud_routing_allowed,
    ingest_allowed,
    load_runtime_controls,
    reload_runtime_controls,
)
from app.models.controls_models import RuntimeControlsUpdate, RuntimeDefaults


def test_load_runtime_controls_from_repo_file():
    controls = load_runtime_controls(force_reload=True)
    assert "cloud_routing" in controls.feature_flags
    assert controls.source_path


def test_cloud_routing_blocked_by_kill_switch(tmp_path, monkeypatch):
    controls_path = tmp_path / "runtime-controls.yaml"
    controls_path.write_text(
        yaml.safe_dump(
            {
                "defaults": {"cloud_routing_enabled": True},
                "feature_flags": {"cloud_routing": True},
                "kill_switches": {"cloud_routing": True},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("APP_RUNTIME_CONTROLS_PATH", str(controls_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    reload_runtime_controls()
    assert cloud_routing_allowed() is False
    get_settings.cache_clear()


def test_apply_runtime_controls_update(tmp_path, monkeypatch):
    controls_path = tmp_path / "runtime-controls.yaml"
    controls_path.write_text(yaml.safe_dump({"feature_flags": {"cloud_routing": False}}), encoding="utf-8")
    monkeypatch.setenv("APP_RUNTIME_CONTROLS_PATH", str(controls_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    updated = apply_runtime_controls_update(
        RuntimeControlsUpdate(feature_flags={"cloud_routing": True}),
    )
    assert updated.feature_flags["cloud_routing"] is True
    assert Path(controls_path).exists()
    get_settings.cache_clear()


def test_ingest_allowed_respects_read_only(monkeypatch):
    monkeypatch.setenv("APP_READ_ONLY", "true")
    from app.core.config import get_settings

    get_settings.cache_clear()
    load_runtime_controls(force_reload=True)
    assert ingest_allowed() is False
    get_settings.cache_clear()
