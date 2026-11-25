"""Shared API dependencies."""

from app.core.auth import UserContext, get_current_user, require_admin_user
from app.models.metrics import Role

# Re-export auth dependencies; legacy X-Role admin check retained for ingest backward compatibility.
require_admin = require_admin_user

__all__ = ["UserContext", "get_current_user", "require_admin", "require_admin_user", "Role"]
