from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status

from app.db.orm import session_scope
from app.domains.auth import repository
from app.lib.security import SESSION_COOKIE_NAME


APP_ROLES = frozenset({"admin", "inventario", "ventas", "reportes", "cliente"})

ROLE_PERMISSIONS = {
    "inventario": frozenset({"products:read", "products:write", "inventory:read", "inventory:write"}),
    "ventas": frozenset({"products:read", "sales:read", "sales:status"}),
    "reportes": frozenset({"sales:read", "reports:read"}),
    "cliente": frozenset({"orders:own"}),
}


def role_has_permission(role_name: str, permission: str) -> bool:
    if role_name == "admin":
        return True
    if role_name not in APP_ROLES:
        return False
    return permission in ROLE_PERMISSIONS.get(role_name, frozenset())


def _fetch_session_user(raw_token: str | None) -> dict | None:
    if not raw_token:
        return None

    with session_scope() as session:
        return repository.get_session_user(session, raw_token)


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


def require_permission(permission: str) -> Callable:
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if not role_has_permission(user["rol"], permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operacion.",
            )
        return user

    return dependency


def require_any_permission(permissions: list[str] | tuple[str, ...]) -> Callable:
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if not any(role_has_permission(user["rol"], permission) for permission in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operacion.",
            )
        return user

    return dependency
