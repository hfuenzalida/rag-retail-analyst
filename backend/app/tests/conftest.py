"""Shared pytest fixtures."""

import os

os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.db.connection import close_pool
from app.models.query_models import DateRange, QueryFilters


@pytest.fixture(autouse=True)
def reset_connection_pool():
    yield
    close_pool()


@pytest.fixture
def may_window() -> DateRange:
    return DateRange(start_date=__import__("datetime").date(2026, 5, 1), end_date=__import__("datetime").date(2026, 5, 31))


@pytest.fixture
def mock_connection():
    conn = MagicMock()
    return conn


@pytest.fixture
def patch_connection(mock_connection):
    @contextmanager
    def _cm():
        yield mock_connection

    return _cm
