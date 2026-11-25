"""Authentication endpoints."""

from fastapi import APIRouter

from app.core.auth import create_access_token
from app.models.eval_models import AuthTokenRequest, AuthTokenResponse
from app.models.metrics import Role

router = APIRouter()


@router.post("/token", response_model=AuthTokenResponse)
async def issue_dev_token(request: AuthTokenRequest) -> AuthTokenResponse:
    """Issue a short-lived JWT for local/staging use. Replace with OIDC in production."""
    role: Role = request.role  # type: ignore[assignment]
    token = create_access_token(client_id=request.client_id, role=role, user_id=request.user_id)
    return AuthTokenResponse(
        access_token=token,
        client_id=request.client_id,
        role=request.role,
    )
