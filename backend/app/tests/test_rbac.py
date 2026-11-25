"""RBAC enforcement tests."""

import pytest

from app.tools.metrics_tools import run_metric_query
from app.tools.rbac import PermissionDeniedError, assert_metric_allowed


def test_manager_can_access_total_revenue():
    assert_metric_allowed("total_revenue", "manager")


def test_manager_denied_gross_margin():
    with pytest.raises(PermissionDeniedError):
        assert_metric_allowed("gross_margin_pct", "manager")


def test_analyst_can_access_gross_margin():
    assert_metric_allowed("gross_margin_pct", "analyst")


def test_run_metric_query_rbac_blocks_manager_margin():
    with pytest.raises(PermissionDeniedError):
        run_metric_query("gross_margin_pct", "demo-retail", "manager")
