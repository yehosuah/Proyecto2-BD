from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.db import procedures
from app.db.connection import get_connection
from app.dependencies.auth import require_permission


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
def low_stock(admin: dict = Depends(require_permission("inventory:read"))) -> dict:
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
def create_adjustment(payload: InventoryAdjustmentPayload, admin: dict = Depends(require_permission("inventory:write"))) -> dict:
    with get_connection() as conn:
        try:
            product = conn.execute(
                "SELECT id_producto FROM producto WHERE id_producto = %s",
                (payload.id_producto,),
            ).fetchone()
            if not product:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
            created = procedures.apply_inventory_adjustment(
                conn,
                product_id=payload.id_producto,
                admin_id=admin["id_usuario"],
                cantidad_delta=payload.cantidad_delta,
                motivo=payload.motivo,
            )
            if not created:
                conn.rollback()
                raise HTTPException(status_code=409, detail="El ajuste dejaria stock negativo.")
            conn.commit()
        except HTTPException:
            raise
        except Exception:
            conn.rollback()
            raise
    return created


@router.post("/restocks", status_code=status.HTTP_201_CREATED)
def create_restock(payload: RestockPayload, admin: dict = Depends(require_permission("inventory:write"))) -> dict:
    if not payload.detalles:
        raise HTTPException(status_code=422, detail="Debes incluir detalles de reabastecimiento.")
    with get_connection() as conn:
        try:
            restock = procedures.create_restock(
                conn,
                provider_id=payload.id_proveedor,
                admin_id=admin["id_usuario"],
                nota=payload.nota,
            )
            detalles = []
            for detail in payload.detalles:
                created_detail = procedures.add_restock_detail(
                    conn,
                    restock_id=restock["id_reabastecimiento"],
                    product_id=detail.id_producto,
                    cantidad=detail.cantidad,
                    costo_unitario=detail.costo_unitario,
                )
                if not created_detail:
                    conn.rollback()
                    raise HTTPException(
                        status_code=409,
                        detail="No se pudo agregar un detalle de reabastecimiento.",
                    )
                detalles.append(created_detail)
            restock["detalles"] = detalles
            conn.commit()
        except HTTPException:
            raise
        except Exception:
            conn.rollback()
            raise
    return restock
