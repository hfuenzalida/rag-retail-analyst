"""Runtime controls admin endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import UserContext, require_admin_user
from app.core.runtime_controls import (
    apply_runtime_controls_update,
    ingest_allowed,
    load_runtime_controls,
    reload_runtime_controls,
)
from app.core.rollout import rollout_summary
from app.models.controls_models import RuntimeControlsSnapshot, RuntimeControlsUpdate

router = APIRouter()


@router.get("/runtime", response_model=RuntimeControlsSnapshot)
async def get_runtime_controls(_: UserContext = Depends(require_admin_user)) -> RuntimeControlsSnapshot:
    """Return current runtime controls and feature flags."""
    return load_runtime_controls()


@router.patch("/runtime", response_model=RuntimeControlsSnapshot)
async def patch_runtime_controls(
    update: RuntimeControlsUpdate,
    _: UserContext = Depends(require_admin_user),
) -> RuntimeControlsSnapshot:
    """Update hot-swappable runtime controls without redeploy."""
    return apply_runtime_controls_update(update)


@router.post("/runtime/reload", response_model=RuntimeControlsSnapshot)
async def reload_controls(_: UserContext = Depends(require_admin_user)) -> RuntimeControlsSnapshot:
    """Force reload controls from disk."""
    return reload_runtime_controls()


@router.get("/rollout")
async def get_rollout_matrix(_: UserContext = Depends(require_admin_user)) -> dict:
    """Return role-based progressive rollout matrix."""
    return rollout_summary()


@router.get("/runtime/ingest-allowed")
async def get_ingest_allowed() -> dict[str, bool]:
    """Public probe for whether ingestion is enabled in this environment."""
    return {"ingest_allowed": ingest_allowed()}
