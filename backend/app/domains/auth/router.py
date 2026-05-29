from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.db.orm import session_scope
from app.dependencies.auth import get_optional_user
from app.domains.auth import repository
from app.lib.security import (
    SESSION_COOKIE_NAME,
    SESSION_DURATION_DAYS,
    hash_password,
    make_session_record,
    verify_password,
)


router = APIRouter()


class RegisterPayload(BaseModel):
    email: str
    password: str
    nombre: str
    apellido: str
    telefono: str | None = None


class LoginPayload(BaseModel):
    email: str
    password: str


def _serialize_user(user: dict) -> dict:
    return {
        "id_usuario": user["id_usuario"],
        "email": user["email"],
        "nombre": user["nombre"],
        "apellido": user["apellido"],
        "telefono": user["telefono"],
        "rol": user["rol"],
    }


def _start_session(response: Response, user_id: int) -> None:
    session_id, token_hash, expires_at, raw_token = make_session_record()
    with session_scope() as session:
        repository.create_user_session(
            session,
            session_id=session_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
    response.set_cookie(
        SESSION_COOKIE_NAME,
        raw_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=int(timedelta(days=SESSION_DURATION_DAYS).total_seconds()),
        path="/",
    )


@router.get("/health")
def auth_health() -> dict[str, str]:
    return {"status": "ok", "domain": "auth"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterPayload, response: Response) -> dict:
    with session_scope() as session:
        if repository.email_exists(session, payload.email):
            raise HTTPException(status_code=409, detail="El email ya esta registrado.")

        created = repository.create_customer_user(
            session,
            email=payload.email,
            password_hash=hash_password(payload.password),
            nombre=payload.nombre,
            apellido=payload.apellido,
            telefono=payload.telefono,
        )

    _start_session(response, created["id_usuario"])
    return {"user": _serialize_user(created)}


@router.post("/login")
def login(payload: LoginPayload, response: Response) -> dict:
    with session_scope() as session:
        user_record = repository.get_user_by_email(session, payload.email)

    if not user_record:
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    user, role_name = user_record
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    _start_session(response, user.id_usuario)
    return {"user": _serialize_user(repository.serialize_user(user, role_name))}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_user: dict | None = Depends(get_optional_user),
) -> Response:
    if session_user:
        with session_scope() as session:
            repository.revoke_user_sessions(session, session_user["id_usuario"])
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/session")
def session_lookup(session_user: dict | None = Depends(get_optional_user)) -> dict:
    if not session_user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": _serialize_user(session_user)}
