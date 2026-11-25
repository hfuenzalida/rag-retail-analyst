"""JWT authentication helpers."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.models.metrics import Role


@dataclass
class UserContext:
    user_id: str
    client_id: str
    role: Role


def create_access_token(
    client_id: str,
    role: Role,
    user_id: str = "dev-user",
    settings: Settings | None = None,
    expires_minutes: int = 60,
) -> str:
    cfg = settings or get_settings()
    secret = cfg.auth_jwt_secret.get_secret_value()
    payload = {
        "sub": user_id,
        "client_id": client_id,
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str, settings: Settings | None = None) -> UserContext:
    cfg = settings or get_settings()
    secret = cfg.auth_jwt_secret.get_secret_value()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return UserContext(
        user_id=str(payload.get("sub", "unknown")),
        client_id=str(payload["client_id"]),
        role=payload["role"],
    )


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_role: Annotated[Role, Header(alias="X-Role")] = "manager",
    x_client_id: Annotated[str | None, Header(alias="X-Client-Id")] = None,
) -> UserContext:
    """Resolve user from Bearer JWT, or dev headers as fallback."""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        return decode_access_token(token)

    return UserContext(
        user_id="header-user",
        client_id=x_client_id or "demo-retail",
        role=x_role,
    )


async def require_admin_user(user: Annotated[UserContext, Depends(get_current_user)]) -> UserContext:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    return user
