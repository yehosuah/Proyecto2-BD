from datetime import datetime, UTC

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.models import Rol, SesionUsuario, Usuario
from app.lib.security import hash_session_token


def serialize_user(user: Usuario, role_name: str) -> dict:
    return {
        "id_usuario": user.id_usuario,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "telefono": user.telefono,
        "rol": role_name,
    }


def get_user_by_email(session: Session, email: str) -> tuple[Usuario, str] | None:
    row = session.execute(
        select(Usuario, Rol.nombre)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
        .where(Usuario.email == email.lower(), Usuario.activo.is_(True))
    ).one_or_none()
    if not row:
        return None
    user, role_name = row
    return user, role_name


def email_exists(session: Session, email: str) -> bool:
    return session.scalar(select(Usuario.id_usuario).where(Usuario.email == email.lower()).limit(1)) is not None


def create_customer_user(
    session: Session,
    *,
    email: str,
    password_hash: str,
    nombre: str,
    apellido: str,
    telefono: str | None,
) -> dict:
    role_id = session.scalar(select(Rol.id_rol).where(Rol.nombre == "cliente"))
    user = Usuario(
        id_rol=role_id,
        email=email.lower(),
        password_hash=password_hash,
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,
        activo=True,
    )
    session.add(user)
    session.flush()
    return serialize_user(user, "cliente")


def create_user_session(
    session: Session,
    *,
    session_id: str,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> None:
    session.add(
        SesionUsuario(
            id_sesion=session_id,
            id_usuario=user_id,
            token_hash=token_hash,
            expira_en=expires_at.replace(tzinfo=None) if expires_at.tzinfo else expires_at,
        )
    )


def get_session_user(session: Session, raw_token: str | None) -> dict | None:
    if not raw_token:
        return None
    now = datetime.now(UTC).replace(tzinfo=None)
    row = session.execute(
        select(SesionUsuario.id_sesion, Usuario, Rol.nombre)
        .join(Usuario, Usuario.id_usuario == SesionUsuario.id_usuario)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
        .where(
            SesionUsuario.token_hash == hash_session_token(raw_token),
            SesionUsuario.revocada_en.is_(None),
            SesionUsuario.expira_en > now,
            Usuario.activo.is_(True),
        )
    ).one_or_none()
    if not row:
        return None
    session_id, user, role_name = row
    result = serialize_user(user, role_name)
    result["id_sesion"] = session_id
    return result


def revoke_user_sessions(session: Session, user_id: int) -> int:
    result = session.execute(
        update(SesionUsuario)
        .where(SesionUsuario.id_usuario == user_id, SesionUsuario.revocada_en.is_(None))
        .values(revocada_en=datetime.now(UTC).replace(tzinfo=None))
    )
    return result.rowcount or 0
