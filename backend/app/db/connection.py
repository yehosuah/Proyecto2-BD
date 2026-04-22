from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import connect
from psycopg.rows import dict_row

from app.config import get_settings


def make_database_dsn() -> str:
    return get_settings().database_url


@contextmanager
def get_connection(*, autocommit: bool = False) -> Iterator:
    conn = connect(
        make_database_dsn(),
        autocommit=autocommit,
        row_factory=dict_row,
    )
    try:
        yield conn
    finally:
        conn.close()
