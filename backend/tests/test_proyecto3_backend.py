from datetime import datetime, timedelta, UTC

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.lib.security import hash_session_token


def _sqlite_session():
    from app.db.models import Base

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_auth_repository_uses_orm_for_user_and_session_crud():
    from app.db.models import Rol, SesionUsuario, Usuario
    from app.domains.auth import repository

    session = _sqlite_session()
    session.add(Rol(id_rol=1, nombre="cliente"))
    session.commit()

    user = repository.create_customer_user(
        session,
        email="orm-cliente@example.test",
        password_hash="sha256:test",
        nombre="Orm",
        apellido="Cliente",
        telefono="5555-0101",
    )
    session.commit()

    stored_user = session.get(Usuario, user["id_usuario"])
    assert stored_user is not None
    assert stored_user.email == "orm-cliente@example.test"

    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    repository.create_user_session(
        session,
        session_id="session-1",
        user_id=user["id_usuario"],
        token_hash=hash_session_token("raw-token"),
        expires_at=expires_at,
    )
    session.commit()

    session_user = repository.get_session_user(session, "raw-token")
    assert session_user is not None
    assert session_user["email"] == "orm-cliente@example.test"
    assert session_user["rol"] == "cliente"

    revoked = repository.revoke_user_sessions(session, user["id_usuario"])
    session.commit()

    assert revoked == 1
    stored_session = session.get(SesionUsuario, "session-1")
    assert stored_session.revocada_en is not None
    assert repository.get_session_user(session, "raw-token") is None


def test_category_create_calls_stored_procedure_and_fetches_created_row():
    from app.db import procedures

    class FakeResult:
        def __init__(self, row):
            self.row = row

        def fetchone(self):
            return self.row

    class FakeConnection:
        def __init__(self):
            self.calls = []
            self.results = [
                {"o_id_categoria": 42},
                {
                    "id_categoria": 42,
                    "nombre": "Audio",
                    "descripcion": "Equipo de sonido",
                    "activa": True,
                },
            ]

        def execute(self, sql, params=None):
            self.calls.append((" ".join(sql.split()), params))
            return FakeResult(self.results.pop(0))

    conn = FakeConnection()

    row = procedures.create_category(
        conn,
        nombre="Audio",
        descripcion="Equipo de sonido",
        activa=True,
    )

    assert conn.calls[0] == (
        "CALL sp_create_category(%s::text, %s::text, %s::boolean, %s::bigint)",
        ("Audio", "Equipo de sonido", True, None),
    )
    assert conn.calls[1] == (
        "SELECT id_categoria, nombre, descripcion, activa FROM categoria WHERE id_categoria = %s",
        (42,),
    )
    assert row["id_categoria"] == 42


def test_role_permission_matrix_matches_project_three_roles():
    from app.dependencies.auth import APP_ROLES, role_has_permission

    assert APP_ROLES == frozenset({"admin", "inventario", "ventas", "reportes", "cliente"})
    assert role_has_permission("admin", "products:write") is True
    assert role_has_permission("inventario", "inventory:write") is True
    assert role_has_permission("inventario", "products:write") is True
    assert role_has_permission("ventas", "sales:status") is True
    assert role_has_permission("ventas", "products:write") is False
    assert role_has_permission("reportes", "reports:read") is True
    assert role_has_permission("reportes", "sales:status") is False
    assert role_has_permission("cliente", "orders:own") is True
    assert role_has_permission("catalogo", "products:read") is False
