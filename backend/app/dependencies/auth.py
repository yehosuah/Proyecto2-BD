from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status

from app.db.connection import get_connection
from app.lib.security import SESSION_COOKIE_NAME, hash_session_token


def _fetch_session_user(raw_token: str | None) -> dict | None:
    if not raw_token:
        return None

    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                s.id_sesion,
                u.id_usuario,
                u.email,
                u.nombre,
                u.apellido,
                u.telefono,
                r.nombre AS rol
            FROM sesion_usuario s
            JOIN usuario u ON u.id_usuario = s.id_usuario
            JOIN rol r ON r.id_rol = u.id_rol
            WHERE s.token_hash = %s
              AND s.revocada_en IS NULL
              AND s.expira_en > CURRENT_TIMESTAMP
              AND u.activo = TRUE
            """,
            (hash_session_token(raw_token),),
        ).fetchone()


def get_optional_user(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> dict | None:
    return _fetch_session_user(session_token)


def get_current_user(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> dict:
    user = _fetch_session_user(session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion no valida.",
        )
    return user


def require_role(role_name: str) -> Callable:
    return require_any_role([role_name])


def require_any_role(role_names: list[str] | tuple[str, ...]) -> Callable:
    allowed_roles = set(role_names)

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user["rol"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operacion.",
            )
        return user

    return dependency
