from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.db.connection import get_connection
from app.dependencies.auth import require_role


router = APIRouter()


class InventoryAdjustmentPayload(BaseModel):
    id_producto: int
    cantidad_delta: int
    motivo: str


class RestockDetailPayload(BaseModel):
    id_producto: int
    cantidad: int = Field(gt=0)
    costo_unitario: float = Field(ge=0)


class RestockPayload(BaseModel):
    id_proveedor: int | None = None
    nota: str | None = None
    detalles: list[RestockDetailPayload]


@router.get("/health")
def inventory_health() -> dict[str, str]:
    return {"status": "ok", "domain": "inventory"}


@router.get("/low-stock")
def low_stock(admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id_producto,
                p.sku,
                p.nombre,
                p.stock_actual,
                (
                    SELECT COALESCE(SUM(dp.cantidad), 0)
                    FROM detalle_pedido dp
                    JOIN pedido pe ON pe.id_pedido = dp.id_pedido
                    WHERE dp.id_producto = p.id_producto
                      AND pe.creado_en >= CURRENT_TIMESTAMP - INTERVAL '30 days'
                ) AS ventas_30_dias
            FROM producto p
            WHERE p.stock_actual <= 10
            ORDER BY p.stock_actual ASC, p.nombre ASC
            """
        ).fetchall()
    return {"items": rows}


@router.post("/adjustments", status_code=status.HTTP_201_CREATED)
def create_adjustment(payload: InventoryAdjustmentPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        product = conn.execute(
            "SELECT id_producto, stock_actual FROM producto WHERE id_producto = %s FOR UPDATE",
            (payload.id_producto,),
        ).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        new_stock = product["stock_actual"] + payload.cantidad_delta
        if new_stock < 0:
            conn.rollback()
            raise HTTPException(status_code=409, detail="El ajuste dejaria stock negativo.")

        created = conn.execute(
            """
            INSERT INTO ajuste_inventario (
                id_producto,
                id_admin,
                cantidad_delta,
                motivo
            )
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (payload.id_producto, admin["id_usuario"], payload.cantidad_delta, payload.motivo),
        ).fetchone()
        conn.execute(
            """
            UPDATE producto
            SET stock_actual = %s,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE id_producto = %s
            """,
            (new_stock, payload.id_producto),
        )
        conn.commit()
    return created


@router.post("/restocks", status_code=status.HTTP_201_CREATED)
def create_restock(payload: RestockPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    if not payload.detalles:
        raise HTTPException(status_code=422, detail="Debes incluir detalles de reabastecimiento.")
    with get_connection() as conn:
        restock = conn.execute(
            """
            INSERT INTO reabastecimiento (
                id_proveedor,
                id_admin,
                nota
            )
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (payload.id_proveedor, admin["id_usuario"], payload.nota),
        ).fetchone()

        for detail in payload.detalles:
            conn.execute(
                """
                INSERT INTO detalle_reabastecimiento (
                    id_reabastecimiento,
                    id_producto,
                    cantidad,
                    costo_unitario
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    restock["id_reabastecimiento"],
                    detail.id_producto,
                    detail.cantidad,
                    detail.costo_unitario,
                ),
            )
            conn.execute(
                """
                UPDATE producto
                SET stock_actual = stock_actual + %s,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id_producto = %s
                """,
                (detail.cantidad, detail.id_producto),
            )
        conn.commit()
    return restock
