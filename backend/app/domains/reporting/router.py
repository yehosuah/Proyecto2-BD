from fastapi import APIRouter, Depends, Query

from app.db.connection import get_connection
from app.dependencies.auth import require_role
from app.lib.queries import build_sales_report_query


router = APIRouter()


@router.get("/health")
def reporting_health() -> dict[str, str]:
    return {"status": "ok", "domain": "reporting"}


@router.get("/snapshot")
def reporting_snapshot(admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        sales_rows = conn.execute(
            build_sales_report_query(),
            {"start_date": None, "end_date": None, "status": None},
        ).fetchall()
        top_rows = conn.execute(
            """
            SELECT
                pr.nombre,
                SUM(dp.cantidad) AS vendidos,
                SUM(dp.cantidad * dp.precio_unitario) AS ingresos
            FROM detalle_pedido dp
            JOIN producto pr ON pr.id_producto = dp.id_producto
            GROUP BY pr.id_producto, pr.nombre
            HAVING SUM(dp.cantidad) > 0
            ORDER BY vendidos DESC, ingresos DESC
            LIMIT 5
            """
        ).fetchall()
    return {"sales": sales_rows, "top_products": top_rows}
