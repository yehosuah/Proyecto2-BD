from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.db.connection import get_connection
from app.dependencies.auth import require_role
from app.lib.queries import build_sales_report_query, export_rows_to_csv


router = APIRouter()


class CategoryPayload(BaseModel):
    nombre: str
    descripcion: str | None = None
    activa: bool = True


class ProductPayload(BaseModel):
    id_categoria: int
    id_proveedor: int | None = None
    sku: str
    nombre: str
    descripcion: str | None = None
    precio_unitario: float = Field(ge=0)
    stock_actual: int = Field(ge=0)
    activo: bool = True


class SalesStatusPayload(BaseModel):
    estado_pedido: str


@router.get("/health")
def admin_health() -> dict[str, str]:
    return {"status": "ok", "domain": "admin"}


@router.get("/categories")
def admin_categories(admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id_categoria, nombre, descripcion, activa
            FROM categoria
            ORDER BY nombre ASC
            """
        ).fetchall()
    return {"items": rows}


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        created = conn.execute(
            """
            INSERT INTO categoria (nombre, descripcion, activa)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (payload.nombre, payload.descripcion, payload.activa),
        ).fetchone()
        conn.commit()
    return created


@router.put("/categories/{category_id}")
def update_category(category_id: int, payload: CategoryPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        updated = conn.execute(
            """
            UPDATE categoria
            SET nombre = %s,
                descripcion = %s,
                activa = %s
            WHERE id_categoria = %s
            RETURNING *
            """,
            (payload.nombre, payload.descripcion, payload.activa, category_id),
        ).fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Categoria no encontrada.")
        conn.commit()
    return updated


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, admin: dict = Depends(require_role("admin"))) -> Response:
    with get_connection() as conn:
        in_use = conn.execute(
            "SELECT 1 FROM producto WHERE id_categoria = %s LIMIT 1",
            (category_id,),
        ).fetchone()
        if in_use:
            raise HTTPException(status_code=409, detail="La categoria tiene productos asociados.")
        deleted = conn.execute(
            "DELETE FROM categoria WHERE id_categoria = %s RETURNING id_categoria",
            (category_id,),
        ).fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Categoria no encontrada.")
        conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/products")
def admin_products(admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id_producto,
                p.id_categoria,
                p.id_proveedor,
                p.sku,
                p.nombre,
                p.descripcion,
                p.precio_unitario,
                p.stock_actual,
                p.activo,
                c.nombre AS categoria_nombre,
                pr.nombre AS proveedor_nombre
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
            ORDER BY p.id_producto ASC
            """
        ).fetchall()
    return {"items": rows}


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        created = conn.execute(
            """
            INSERT INTO producto (
                id_categoria,
                id_proveedor,
                sku,
                nombre,
                descripcion,
                precio_unitario,
                stock_actual,
                activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                payload.id_categoria,
                payload.id_proveedor,
                payload.sku,
                payload.nombre,
                payload.descripcion,
                payload.precio_unitario,
                payload.stock_actual,
                payload.activo,
            ),
        ).fetchone()
        conn.commit()
    return created


@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductPayload, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        updated = conn.execute(
            """
            UPDATE producto
            SET id_categoria = %s,
                id_proveedor = %s,
                sku = %s,
                nombre = %s,
                descripcion = %s,
                precio_unitario = %s,
                stock_actual = %s,
                activo = %s,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE id_producto = %s
            RETURNING *
            """,
            (
                payload.id_categoria,
                payload.id_proveedor,
                payload.sku,
                payload.nombre,
                payload.descripcion,
                payload.precio_unitario,
                payload.stock_actual,
                payload.activo,
                product_id,
            ),
        ).fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        conn.commit()
    return updated


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, admin: dict = Depends(require_role("admin"))) -> Response:
    with get_connection() as conn:
        in_use = conn.execute(
            "SELECT 1 FROM detalle_pedido WHERE id_producto = %s LIMIT 1",
            (product_id,),
        ).fetchone()
        if in_use:
            raise HTTPException(status_code=409, detail="El producto ya tiene ventas asociadas.")
        deleted = conn.execute(
            "DELETE FROM producto WHERE id_producto = %s RETURNING id_producto",
            (product_id,),
        ).fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sales")
def list_sales(
    status_filter: str | None = Query(default=None),
    admin: dict = Depends(require_role("admin")),
) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.codigo_publico,
                p.creado_en,
                p.nombre_cliente,
                p.tipo_entrega,
                p.estado_pedido,
                p.estado_pago,
                pa.metodo AS pago_metodo,
                COALESCE(v.total_pedido, 0) AS total_pedido
            FROM pedido p
            JOIN pago pa ON pa.id_pedido = p.id_pedido
            LEFT JOIN vw_resumen_ventas v ON v.id_pedido = p.id_pedido
            WHERE (%s::text IS NULL OR p.estado_pedido = %s::text)
            ORDER BY p.creado_en DESC
            """,
            (status_filter, status_filter),
        ).fetchall()
    return {"items": rows}


@router.get("/sales/{codigo_publico}")
def get_sale_detail(codigo_publico: str, admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        order = conn.execute(
            """
            SELECT
                p.id_pedido,
                p.codigo_publico,
                p.nombre_cliente,
                p.email_cliente,
                p.telefono_cliente,
                p.tipo_entrega,
                p.estado_pedido,
                p.estado_pago,
                p.nota_cliente,
                p.creado_en,
                pa.metodo,
                pa.monto,
                pa.estado AS pago_estado,
                pa.codigo_simulado
            FROM pedido p
            JOIN pago pa ON pa.id_pedido = p.id_pedido
            WHERE p.codigo_publico = %s
            """,
            (codigo_publico,),
        ).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Venta no encontrada.")
        items = conn.execute(
            """
            SELECT
                dp.id_detalle_pedido,
                pr.sku,
                pr.nombre,
                dp.cantidad,
                dp.precio_unitario
            FROM detalle_pedido dp
            JOIN producto pr ON pr.id_producto = dp.id_producto
            WHERE dp.id_pedido = %s
            ORDER BY dp.id_detalle_pedido
            """,
            (order["id_pedido"],),
        ).fetchall()
    return {"order": order, "items": items}


@router.patch("/sales/{codigo_publico}")
def update_sale_status(
    codigo_publico: str,
    payload: SalesStatusPayload,
    admin: dict = Depends(require_role("admin")),
) -> dict:
    with get_connection() as conn:
        updated = conn.execute(
            """
            UPDATE pedido
            SET estado_pedido = %s
            WHERE codigo_publico = %s
            RETURNING id_pedido, codigo_publico, estado_pedido
            """,
            (payload.estado_pedido, codigo_publico),
        ).fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Venta no encontrada.")
        conn.execute(
            """
            INSERT INTO historial_estado_pedido (
                id_pedido,
                id_usuario,
                estado_anterior,
                estado_nuevo,
                nota
            )
            VALUES (%s, %s, NULL, %s, 'Cambio manual desde panel admin.')
            """,
            (updated["id_pedido"], admin["id_usuario"], payload.estado_pedido),
        )
        conn.commit()
    return updated


@router.get("/reports/sales")
def sales_report(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    admin: dict = Depends(require_role("admin")),
) -> dict:
    params = {"start_date": start_date, "end_date": end_date, "status": status_filter}
    with get_connection() as conn:
        series = conn.execute(build_sales_report_query(), params).fetchall()
        summary = conn.execute(
            """
            SELECT
                COUNT(*) AS total_ordenes,
                COALESCE(SUM(total_pedido), 0) AS ventas_totales
            FROM vw_resumen_ventas
            WHERE (%(start_date)s::date IS NULL OR DATE(creado_en) >= %(start_date)s::date)
              AND (%(end_date)s::date IS NULL OR DATE(creado_en) <= %(end_date)s::date)
            """,
            params,
        ).fetchone()
    return {"series": series, "summary": summary}


@router.get("/reports/sales/export.csv")
def export_sales_csv(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    admin: dict = Depends(require_role("admin")),
) -> Response:
    params = {"start_date": start_date, "end_date": end_date, "status": status_filter}
    with get_connection() as conn:
        rows = conn.execute(build_sales_report_query(), params).fetchall()
    csv_body = export_rows_to_csv(rows, ["fecha", "ordenes", "ventas_totales"])
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ventas-por-fecha.csv"},
    )


@router.get("/reports/top-products")
def top_products(admin: dict = Depends(require_role("admin"))) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                pr.id_producto,
                pr.nombre,
                pr.sku,
                SUM(dp.cantidad) AS vendidos,
                SUM(dp.cantidad * dp.precio_unitario) AS ingresos
            FROM detalle_pedido dp
            JOIN producto pr ON pr.id_producto = dp.id_producto
            GROUP BY pr.id_producto, pr.nombre, pr.sku
            HAVING SUM(dp.cantidad) > 0
            ORDER BY vendidos DESC, ingresos DESC
            LIMIT 10
            """
        ).fetchall()
    return {"items": rows}


@router.get("/reports/low-stock")
def low_stock_report(admin: dict = Depends(require_role("admin"))) -> dict:
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
                    WHERE dp.id_producto = p.id_producto
                ) AS ventas_historicas
            FROM producto p
            WHERE p.stock_actual <= 10
               OR EXISTS (
                    SELECT 1
                    FROM detalle_pedido dp
                    WHERE dp.id_producto = p.id_producto
                    GROUP BY dp.id_producto
                    HAVING SUM(dp.cantidad) >= 5
               )
            ORDER BY p.stock_actual ASC, ventas_historicas DESC
            """
        ).fetchall()
    return {"items": rows}
