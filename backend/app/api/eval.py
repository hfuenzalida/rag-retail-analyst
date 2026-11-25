"""Evaluation endpoints."""

from fastapi import APIRouter, Depends

from app.agents.evaluator import run_eval_suite
from app.api.deps import require_admin_user
from app.core.auth import UserContext
from app.models.eval_models import EvalRunRequest, GoldenEvalReport

router = APIRouter()


@router.post("/run", response_model=GoldenEvalReport)
async def run_eval(
    request: EvalRunRequest,
    _: UserContext = Depends(require_admin_user),
) -> GoldenEvalReport:
    """Run golden-question evaluation for a client (admin only)."""
    return run_eval_suite(client_id=request.client_id, subset=request.subset)
