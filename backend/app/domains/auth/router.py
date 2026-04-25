from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.db.connection import get_connection
from app.dependencies.auth import get_optional_user
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
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sesion_usuario (
                id_sesion,
                id_usuario,
                token_hash,
                expira_en
            ) VALUES (%s, %s, %s, %s)
            """,
            (session_id, user_id, token_hash, expires_at),
        )
        conn.commit()
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
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id_usuario FROM usuario WHERE email = %s",
            (payload.email.lower(),),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="El email ya esta registrado.")

        created = conn.execute(
            """
            INSERT INTO usuario (
                id_rol,
                email,
                password_hash,
                nombre,
                apellido,
                telefono
            )
            VALUES (
                (SELECT id_rol FROM rol WHERE nombre = 'cliente'),
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id_usuario, email, nombre, apellido, telefono
            """,
            (
                payload.email.lower(),
                hash_password(payload.password),
                payload.nombre,
                payload.apellido,
                payload.telefono,
            ),
        ).fetchone()
        conn.commit()

    _start_session(response, created["id_usuario"])
    created["rol"] = "cliente"
    return {"user": _serialize_user(created)}


@router.post("/login")
def login(payload: LoginPayload, response: Response) -> dict:
    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT
                u.id_usuario,
                u.email,
                u.password_hash,
                u.nombre,
                u.apellido,
                u.telefono,
                r.nombre AS rol
            FROM usuario u
            JOIN rol r ON r.id_rol = u.id_rol
            WHERE u.email = %s
              AND u.activo = TRUE
            """,
            (payload.email.lower(),),
        ).fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    _start_session(response, user["id_usuario"])
    return {"user": _serialize_user(user)}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_user: dict | None = Depends(get_optional_user),
) -> Response:
    if session_user:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE sesion_usuario
                SET revocada_en = CURRENT_TIMESTAMP
                WHERE id_usuario = %s
                  AND revocada_en IS NULL
                """,
                (session_user["id_usuario"],),
            )
            conn.commit()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/session")
def session_lookup(session_user: dict | None = Depends(get_optional_user)) -> dict:
    if not session_user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": _serialize_user(session_user)}
