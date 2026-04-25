from fastapi import APIRouter, HTTPException, Query

from app.db.connection import get_connection


router = APIRouter()


@router.get("/health")
def catalog_health() -> dict[str, str]:
    return {"status": "ok", "domain": "catalog"}


@router.get("/categories")
def list_categories() -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id_categoria,
                c.nombre,
                c.descripcion,
                c.activa,
                COUNT(p.id_producto) AS total_productos
            FROM categoria c
            LEFT JOIN producto p ON p.id_categoria = c.id_categoria AND p.activo = TRUE
            GROUP BY c.id_categoria
            ORDER BY c.nombre ASC
            """
        ).fetchall()
    return {"items": rows}


@router.get("/products")
def list_products(
    category_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> dict:
    search_term = f"%{search.lower()}%" if search else None
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id_producto,
                p.sku,
                p.nombre,
                p.descripcion,
                p.precio_unitario,
                p.stock_actual,
                p.activo,
                c.id_categoria,
                c.nombre AS categoria_nombre,
                pr.id_proveedor,
                pr.nombre AS proveedor_nombre,
                (
                    SELECT COALESCE(SUM(dp.cantidad), 0)
                    FROM detalle_pedido dp
                    WHERE dp.id_producto = p.id_producto
                ) AS unidades_vendidas
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
            WHERE (%s::bigint IS NULL OR p.id_categoria = %s::bigint)
              AND (
                    %s::text IS NULL
                    OR LOWER(p.nombre) LIKE %s::text
                    OR LOWER(p.sku) LIKE %s::text
                  )
            ORDER BY p.id_producto ASC
            """,
            (category_id, category_id, search_term, search_term, search_term),
        ).fetchall()
    return {"items": rows}


@router.get("/products/{sku}")
def get_product(sku: str) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                p.id_producto,
                p.sku,
                p.nombre,
                p.descripcion,
                p.precio_unitario,
                p.stock_actual,
                p.activo,
                c.id_categoria,
                c.nombre AS categoria_nombre,
                pr.id_proveedor,
                pr.nombre AS proveedor_nombre
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
            WHERE p.sku = %s
            """,
            (sku,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return row
