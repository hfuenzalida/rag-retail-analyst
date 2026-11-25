"""Role-based progressive rollout matrix."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.runtime_controls import load_runtime_controls
from app.models.metrics import Role

DEFAULT_ROLLOUT: dict[str, dict[str, bool]] = {
    "cloud_routing": {"admin": True, "analyst": True, "manager": False},
    "new_prompts": {"admin": True, "analyst": True, "manager": False},
    "recommendation_engine": {"admin": True, "analyst": True, "manager": True},
    "deep_dive_mode": {"admin": True, "analyst": True, "manager": False},
    "driver_analysis": {"admin": True, "analyst": True, "manager": False},
}


def get_rollout_matrix(settings: Settings | None = None) -> dict[str, dict[str, bool]]:
    controls = load_runtime_controls(settings=settings)
    matrix = {feature: dict(roles) for feature, roles in DEFAULT_ROLLOUT.items()}
    for feature, roles in (controls.rollout or {}).items():
        matrix.setdefault(feature, {})
        matrix[feature].update({str(role): bool(enabled) for role, enabled in roles.items()})
    return matrix


def is_feature_available_for_role(feature: str, role: Role, settings: Settings | None = None) -> bool:
    matrix = get_rollout_matrix(settings)
    role_map = matrix.get(feature, DEFAULT_ROLLOUT.get(feature, {}))
    return role_map.get(role, False)


def rollout_summary(settings: Settings | None = None) -> dict:
    cfg = settings or get_settings()
    matrix = get_rollout_matrix(cfg)
    return {
        "environment": cfg.app_env,
        "matrix": matrix,
        "stages": [
            {"stage": "internal", "roles": ["admin"], "description": "Full visibility in staging/production admin"},
            {"stage": "analysts", "roles": ["analyst"], "description": "Deep-dive, drivers, cloud routing"},
            {"stage": "managers", "roles": ["manager"], "description": "Summary metrics and recommendations"},
        ],
    }
