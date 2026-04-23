from app.config import get_settings


def make_database_dsn() -> str:
    return get_settings().database_url

