"""Hot-swappable runtime controls loaded from YAML."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

import yaml

from app.core.config import Settings, get_settings
from app.models.controls_models import RuntimeControlsSnapshot, RuntimeControlsUpdate, RuntimeDefaults

_lock = Lock()
_cached: RuntimeControlsSnapshot | None = None

DEFAULT_CONTROLS: dict = {
    "defaults": {
        "local_llm_model": "llama3.2",
        "cloud_routing_enabled": False,
        "eval_sampling_rate": 0.05,
    },
    "sensitivity": {
        "high_keywords": ["customer", "salary", "patient"],
        "default_decision": "local_only",
    },
    "feature_flags": {
        "cloud_routing": False,
        "recommendation_engine": True,
        "new_prompts": False,
        "ingest_enabled": True,
    },
    "kill_switches": {
        "cloud_routing": False,
        "automated_recommendations": False,
        "local_llm": False,
        "openai_provider": False,
        "new_prompts": False,
    },
    "rollout": {
        "cloud_routing": {"admin": True, "analyst": True, "manager": False},
        "new_prompts": {"admin": True, "analyst": True, "manager": False},
        "recommendation_engine": {"admin": True, "analyst": True, "manager": True},
        "deep_dive_mode": {"admin": True, "analyst": True, "manager": False},
        "driver_analysis": {"admin": True, "analyst": True, "manager": False},
    },
}


def resolve_controls_path(settings: Settings | None = None) -> Path:
    cfg = settings or get_settings()
    if cfg.runtime_controls_path:
        return Path(cfg.runtime_controls_path)
    return Path(__file__).resolve().parents[3] / "infra" / "flags" / "runtime-controls.yaml"


def _merge_defaults(raw: dict) -> dict:
    merged = {**DEFAULT_CONTROLS}
    for key in ("defaults", "sensitivity", "feature_flags", "kill_switches", "rollout"):
        if key in raw:
            if key == "rollout":
                merged[key] = {**merged.get(key, {}), **raw[key]}
            else:
                merged[key] = {**merged.get(key, {}), **raw[key]}
    return merged


def load_runtime_controls(*, force_reload: bool = False, settings: Settings | None = None) -> RuntimeControlsSnapshot:
    global _cached
    with _lock:
        if _cached is not None and not force_reload:
            return _cached

        path = resolve_controls_path(settings)
        raw = DEFAULT_CONTROLS.copy()
        if path.exists():
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            raw = _merge_defaults(loaded)

        _cached = RuntimeControlsSnapshot(source_path=str(path), **raw)
        return _cached


def reload_runtime_controls(settings: Settings | None = None) -> RuntimeControlsSnapshot:
    return load_runtime_controls(force_reload=True, settings=settings)


def is_feature_enabled(name: str, *, default: bool = False, settings: Settings | None = None) -> bool:
    controls = load_runtime_controls(settings=settings)
    return controls.feature_flags.get(name, default)


def is_kill_switch_active(name: str, *, settings: Settings | None = None) -> bool:
    controls = load_runtime_controls(settings=settings)
    return controls.kill_switches.get(name, False)


def cloud_routing_allowed(settings: Settings | None = None) -> bool:
    controls = load_runtime_controls(settings=settings)
    if controls.kill_switches.get("cloud_routing", False):
        return False
    return controls.feature_flags.get("cloud_routing", False) or controls.defaults.cloud_routing_enabled


def apply_runtime_controls_update(update: RuntimeControlsUpdate, settings: Settings | None = None) -> RuntimeControlsSnapshot:
    path = resolve_controls_path(settings)
    current = load_runtime_controls(settings=settings)
    payload = {
        "defaults": current.defaults.model_dump(),
        "sensitivity": current.sensitivity.model_dump(),
        "feature_flags": dict(current.feature_flags),
        "kill_switches": dict(current.kill_switches),
        "rollout": dict(current.rollout),
    }

    if update.feature_flags:
        payload["feature_flags"].update(update.feature_flags)
    if update.kill_switches:
        payload["kill_switches"].update(update.kill_switches)
    if update.defaults:
        payload["defaults"] = update.defaults.model_dump()
    if update.rollout:
        for feature, roles in update.rollout.items():
            payload["rollout"].setdefault(feature, {})
            payload["rollout"][feature].update(roles)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return reload_runtime_controls(settings=settings)


def ingest_allowed(settings: Settings | None = None) -> bool:
    cfg = settings or get_settings()
    if cfg.read_only or not cfg.enable_ingest:
        return False
    if is_kill_switch_active("ingest", settings=cfg):
        return False
    return is_feature_enabled("ingest_enabled", default=True, settings=cfg)
