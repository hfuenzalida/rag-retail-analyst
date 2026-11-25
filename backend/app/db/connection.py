"""PostgreSQL connection pool."""

from contextlib import contextmanager
from typing import Generator

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import Settings, get_settings

_pool: ConnectionPool | None = None


def init_pool(settings: Settings | None = None) -> ConnectionPool:
    global _pool
    cfg = settings or get_settings()
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=cfg.db_url.get_secret_value(),
            min_size=1,
            max_size=10,
            kwargs={"row_factory": dict_row},
        )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def get_connection(settings: Settings | None = None) -> Generator[Connection, None, None]:
    pool = init_pool(settings)
    with pool.connection() as conn:
        yield conn
