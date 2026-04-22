from datetime import datetime, timedelta, UTC
import hashlib
import secrets
from uuid import uuid4


SESSION_COOKIE_NAME = "tienda_session"
SESSION_DURATION_DAYS = 7


def hash_password(password: str) -> str:
    return f"sha256:{hashlib.sha256(password.encode('utf-8')).hexdigest()}"


def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def make_session_record() -> tuple[str, str, datetime, str]:
    token = generate_session_token()
    token_hash = hash_session_token(token)
    expires_at = datetime.now(UTC) + timedelta(days=SESSION_DURATION_DAYS)
    return str(uuid4()), token_hash, expires_at, token


def generate_order_code() -> str:
    return f"ORD-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def generate_payment_code() -> str:
    return f"PAY-{uuid4().hex[:10].upper()}"

