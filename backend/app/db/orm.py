from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.connection import make_database_dsn


def make_sqlalchemy_url() -> str:
    dsn = make_database_dsn()
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+psycopg://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql+psycopg://", 1)
    return dsn


engine = create_engine(make_sqlalchemy_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
