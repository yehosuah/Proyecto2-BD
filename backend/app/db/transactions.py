from fastapi import HTTPException, status


SERIALIZABLE = "SERIALIZABLE"


def begin_serializable(conn) -> None:
    conn.execute("BEGIN")
    conn.execute(f"SET TRANSACTION ISOLATION LEVEL {SERIALIZABLE}")


def rollback_with_error(conn, detail: str, code: int = status.HTTP_409_CONFLICT) -> None:
    conn.rollback()
    raise HTTPException(status_code=code, detail=detail)
