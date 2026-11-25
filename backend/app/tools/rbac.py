"""Role-based access control for metric tools."""

from app.models.metrics import CANONICAL_METRICS, METRICS_BY_ROLE, Role


class PermissionDeniedError(Exception):
    def __init__(self, metric_name: str, role: Role):
        self.metric_name = metric_name
        self.role = role
        super().__init__(f"Role '{role}' may not access metric '{metric_name}'")


def assert_metric_allowed(metric_name: str, role: Role) -> None:
    if metric_name not in CANONICAL_METRICS:
        raise ValueError(f"Unknown metric: {metric_name}")
    allowed = METRICS_BY_ROLE.get(role, frozenset())
    if metric_name not in allowed:
        raise PermissionDeniedError(metric_name, role)


def assert_dimension_allowed(role: Role) -> None:
    if role == "manager":
        return
    if role in ("analyst", "admin"):
        return
    raise PermissionDeniedError("drivers", role)
