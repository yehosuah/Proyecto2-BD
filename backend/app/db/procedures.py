from typing import Any


def _out(row: dict[str, Any], key: str) -> Any:
    return row[key]


def create_category(conn, *, nombre: str, descripcion: str | None, activa: bool) -> dict:
    result = conn.execute(
        "CALL sp_create_category(%s::text, %s::text, %s::boolean, %s::bigint)",
        (nombre, descripcion, activa, None),
    ).fetchone()
    category_id = _out(result, "o_id_categoria")
    return conn.execute(
        "SELECT id_categoria, nombre, descripcion, activa FROM categoria WHERE id_categoria = %s",
        (category_id,),
    ).fetchone()


def update_category(conn, *, category_id: int, nombre: str, descripcion: str | None, activa: bool) -> dict | None:
    result = conn.execute(
        "CALL sp_update_category(%s::bigint, %s::text, %s::text, %s::boolean, %s::boolean)",
        (category_id, nombre, descripcion, activa, None),
    ).fetchone()
    if not _out(result, "o_found"):
        return None
    return conn.execute(
        "SELECT id_categoria, nombre, descripcion, activa FROM categoria WHERE id_categoria = %s",
        (category_id,),
    ).fetchone()


def create_product(
    conn,
    *,
    id_categoria: int,
    id_proveedor: int | None,
    sku: str,
    nombre: str,
    descripcion: str | None,
    precio_unitario: float,
    stock_actual: int,
    activo: bool,
) -> dict:
    result = conn.execute(
        """
        CALL sp_create_product(
            %s::bigint,
            %s::bigint,
            %s::text,
            %s::text,
            %s::text,
            %s::numeric,
            %s::integer,
            %s::boolean,
            %s::bigint
        )
        """,
        (
            id_categoria,
            id_proveedor,
            sku,
            nombre,
            descripcion,
            precio_unitario,
            stock_actual,
            activo,
            None,
        ),
    ).fetchone()
    product_id = _out(result, "o_id_producto")
    return _fetch_product(conn, product_id)


def update_product(
    conn,
    *,
    product_id: int,
    id_categoria: int,
    id_proveedor: int | None,
    sku: str,
    nombre: str,
    descripcion: str | None,
    precio_unitario: float,
    stock_actual: int,
    activo: bool,
) -> dict | None:
    result = conn.execute(
        """
        CALL sp_update_product(
            %s::bigint,
            %s::bigint,
            %s::bigint,
            %s::text,
            %s::text,
            %s::text,
            %s::numeric,
            %s::integer,
            %s::boolean,
            %s::boolean
        )
        """,
        (
            product_id,
            id_categoria,
            id_proveedor,
            sku,
            nombre,
            descripcion,
            precio_unitario,
            stock_actual,
            activo,
            None,
        ),
    ).fetchone()
    if not _out(result, "o_found"):
        return None
    return _fetch_product(conn, product_id)


def update_sale_status(conn, *, codigo_publico: str, estado_pedido: str, admin_id: int) -> dict | None:
    result = conn.execute(
        "CALL sp_update_sale_status(%s::text, %s::text, %s::bigint, %s::bigint, %s::boolean)",
        (codigo_publico, estado_pedido, admin_id, None, None),
    ).fetchone()
    if not _out(result, "o_found"):
        return None
    return conn.execute(
        """
        SELECT id_pedido, codigo_publico, estado_pedido
        FROM pedido
        WHERE id_pedido = %s
        """,
        (_out(result, "o_id_pedido"),),
    ).fetchone()


def apply_inventory_adjustment(
    conn,
    *,
    product_id: int,
    admin_id: int,
    cantidad_delta: int,
    motivo: str,
) -> dict | None:
    result = conn.execute(
        "CALL sp_apply_inventory_adjustment(%s::bigint, %s::bigint, %s::integer, %s::text, %s::bigint, %s::integer)",
        (product_id, admin_id, cantidad_delta, motivo, None, None),
    ).fetchone()
    adjustment_id = _out(result, "o_id_ajuste")
    if adjustment_id is None:
        return None
    adjustment = conn.execute(
        """
        SELECT id_ajuste, id_producto, id_admin, cantidad_delta, motivo, creado_en
        FROM ajuste_inventario
        WHERE id_ajuste = %s
        """,
        (adjustment_id,),
    ).fetchone()
    if not adjustment:
        return None
    adjustment["stock_actual"] = _out(result, "o_stock_actual")
    return adjustment


def create_restock(conn, *, provider_id: int | None, admin_id: int, nota: str | None) -> dict:
    result = conn.execute(
        "CALL sp_create_restock(%s::bigint, %s::bigint, %s::text, %s::bigint)",
        (provider_id, admin_id, nota, None),
    ).fetchone()
    restock_id = _out(result, "o_id_reabastecimiento")
    return conn.execute(
        """
        SELECT id_reabastecimiento, id_proveedor, id_admin, nota, creado_en
        FROM reabastecimiento
        WHERE id_reabastecimiento = %s
        """,
        (restock_id,),
    ).fetchone()


def add_restock_detail(
    conn,
    *,
    restock_id: int,
    product_id: int,
    cantidad: int,
    costo_unitario: float,
) -> dict | None:
    result = conn.execute(
        "CALL sp_add_restock_detail(%s::bigint, %s::bigint, %s::integer, %s::numeric, %s::bigint, %s::integer)",
        (restock_id, product_id, cantidad, costo_unitario, None, None),
    ).fetchone()
    detail_id = _out(result, "o_id_detalle_reab")
    if detail_id is None:
        return None
    detail = conn.execute(
        """
        SELECT id_detalle_reab, id_reabastecimiento, id_producto, cantidad, costo_unitario
        FROM detalle_reabastecimiento
        WHERE id_detalle_reab = %s
        """,
        (detail_id,),
    ).fetchone()
    if not detail:
        return None
    detail["stock_actual"] = _out(result, "o_stock_actual")
    return detail


def _fetch_product(conn, product_id: int) -> dict:
    return conn.execute(
        """
        SELECT
            id_producto,
            id_categoria,
            id_proveedor,
            sku,
            nombre,
            descripcion,
            precio_unitario,
            stock_actual,
            activo,
            creado_en,
            actualizado_en
        FROM producto
        WHERE id_producto = %s
        """,
        (product_id,),
    ).fetchone()
