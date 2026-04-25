from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.db.connection import get_connection
from app.db.transactions import begin_serializable
from app.dependencies.auth import get_current_user, get_optional_user
from app.lib.security import generate_order_code, generate_payment_code


router = APIRouter()


class CheckoutItem(BaseModel):
    id_producto: int
    cantidad: int = Field(gt=0)


class CustomerPayload(BaseModel):
    nombre: str
    email: str
    telefono: str | None = None


class AddressPayload(BaseModel):
    linea_1: str
    linea_2: str | None = None
    ciudad: str
    departamento: str
    referencia: str | None = None


class PaymentPayload(BaseModel):
    metodo: str
    referencia: str


class CheckoutPayload(BaseModel):
    customer: CustomerPayload
    tipo_entrega: str
    nota_cliente: str | None = None
    direccion: AddressPayload | None = None
    items: list[CheckoutItem]
    payment: PaymentPayload


def _should_reject_payment(payment: PaymentPayload) -> bool:
    marker = payment.referencia.upper()
    if "FAIL" in marker or marker.endswith("0000"):
        return True
    if payment.metodo == "transferencia" and "RECHAZO" in marker:
        return True
    return False


def _format_order_detail(conn, codigo_publico: str) -> dict:
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
            p.confirmado_en,
            u.id_usuario,
            u.email AS usuario_email
        FROM pedido p
        LEFT JOIN usuario u ON u.id_usuario = p.id_usuario
        WHERE p.codigo_publico = %s
        """,
        (codigo_publico,),
    ).fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    items = conn.execute(
        """
        SELECT
            dp.id_detalle_pedido,
            dp.id_producto,
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

    payment = conn.execute(
        """
        SELECT metodo, monto, estado, codigo_simulado, procesado_en
        FROM pago
        WHERE id_pedido = %s
        """,
        (order["id_pedido"],),
    ).fetchone()

    address = conn.execute(
        """
        SELECT linea_1, linea_2, ciudad, departamento, referencia
        FROM direccion_entrega
        WHERE id_pedido = %s
        """,
        (order["id_pedido"],),
    ).fetchone()

    history = conn.execute(
        """
        SELECT estado_anterior, estado_nuevo, nota, creado_en
        FROM historial_estado_pedido
        WHERE id_pedido = %s
        ORDER BY creado_en ASC
        """,
        (order["id_pedido"],),
    ).fetchall()

    return {
        "order": order,
        "items": items,
        "payment": payment,
        "delivery_address": address,
        "history": history,
    }


@router.get("/health")
def orders_health() -> dict[str, str]:
    return {"status": "ok", "domain": "orders"}


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout(payload: CheckoutPayload, session_user: dict | None = Depends(get_optional_user)) -> dict:
    if payload.tipo_entrega not in {"delivery", "pickup"}:
        raise HTTPException(status_code=422, detail="Tipo de entrega invalido.")
    if payload.tipo_entrega == "delivery" and not payload.direccion:
        raise HTTPException(status_code=422, detail="Debes ingresar direccion para delivery.")
    if not payload.items:
        raise HTTPException(status_code=422, detail="El carrito no puede estar vacio.")

    with get_connection() as conn:
        begin_serializable(conn)
        product_ids = [item.id_producto for item in payload.items]
        products = conn.execute(
            """
            SELECT id_producto, sku, nombre, precio_unitario, stock_actual, activo
            FROM producto
            WHERE id_producto = ANY(%s)
            FOR UPDATE
            """,
            (product_ids,),
        ).fetchall()
        product_map = {row["id_producto"]: row for row in products}

        if len(product_map) != len(product_ids):
            conn.rollback()
            raise HTTPException(status_code=404, detail="Uno o mas productos no existen.")

        for item in payload.items:
            product = product_map[item.id_producto]
            if not product["activo"]:
                conn.rollback()
                raise HTTPException(status_code=409, detail=f"El producto {product['nombre']} no esta activo.")
            if product["stock_actual"] < item.cantidad:
                conn.rollback()
                raise HTTPException(
                    status_code=409,
                    detail=f"Stock insuficiente para {product['nombre']}.",
                )

        if _should_reject_payment(payload.payment):
            conn.rollback()
            return JSONResponse(
                status_code=409,
                content={
                    "order": None,
                    "payment": {
                        "estado": "rechazado",
                        "metodo": payload.payment.metodo,
                        "motivo": "Pago simulado rechazado por regla deterministica.",
                    },
                },
            )

        order_code = generate_order_code()
        payment_code = generate_payment_code()
        order_status = "listo_para_retiro" if payload.tipo_entrega == "pickup" else "en_preparacion"

        order = conn.execute(
            """
            INSERT INTO pedido (
                id_usuario,
                codigo_publico,
                nombre_cliente,
                email_cliente,
                telefono_cliente,
                tipo_entrega,
                estado_pedido,
                estado_pago,
                nota_cliente,
                confirmado_en
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'aprobado', %s, CURRENT_TIMESTAMP)
            RETURNING id_pedido, codigo_publico
            """,
            (
                session_user["id_usuario"] if session_user else None,
                order_code,
                payload.customer.nombre,
                payload.customer.email.lower(),
                payload.customer.telefono,
                payload.tipo_entrega,
                order_status,
                payload.nota_cliente,
            ),
        ).fetchone()

        total_amount = 0
        for item in payload.items:
            product = product_map[item.id_producto]
            line_total = float(product["precio_unitario"]) * item.cantidad
            total_amount += line_total
            conn.execute(
                """
                INSERT INTO detalle_pedido (
                    id_pedido,
                    id_producto,
                    cantidad,
                    precio_unitario
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order["id_pedido"],
                    item.id_producto,
                    item.cantidad,
                    product["precio_unitario"],
                ),
            )
            conn.execute(
                """
                UPDATE producto
                SET stock_actual = stock_actual - %s,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id_producto = %s
                """,
                (item.cantidad, item.id_producto),
            )

        conn.execute(
            """
            INSERT INTO pago (
                id_pedido,
                metodo,
                monto,
                estado,
                codigo_simulado,
                procesado_en
            )
            VALUES (%s, %s, %s, 'aprobado', %s, CURRENT_TIMESTAMP)
            """,
            (order["id_pedido"], payload.payment.metodo, total_amount, payment_code),
        )

        conn.execute(
            """
            INSERT INTO historial_estado_pedido (
                id_pedido,
                id_usuario,
                estado_anterior,
                estado_nuevo,
                nota
            )
            VALUES (%s, %s, NULL, %s, %s)
            """,
            (
                order["id_pedido"],
                session_user["id_usuario"] if session_user else None,
                order_status,
                "Pedido creado automaticamente tras pago aprobado.",
            ),
        )

        if payload.direccion:
            conn.execute(
                """
                INSERT INTO direccion_entrega (
                    id_pedido,
                    linea_1,
                    linea_2,
                    ciudad,
                    departamento,
                    referencia
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    order["id_pedido"],
                    payload.direccion.linea_1,
                    payload.direccion.linea_2,
                    payload.direccion.ciudad,
                    payload.direccion.departamento,
                    payload.direccion.referencia,
                ),
            )

        conn.commit()
        return _format_order_detail(conn, order["codigo_publico"])


@router.get("/me")
def list_my_orders(user: dict = Depends(get_current_user)) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id_pedido,
                p.codigo_publico,
                p.tipo_entrega,
                p.estado_pedido,
                p.estado_pago,
                p.creado_en,
                COALESCE(v.total_pedido, 0) AS total_pedido
            FROM pedido p
            LEFT JOIN vw_resumen_ventas v ON v.id_pedido = p.id_pedido
            WHERE p.id_usuario = %s
            ORDER BY p.creado_en DESC
            """,
            (user["id_usuario"],),
        ).fetchall()
    return {"items": rows}


@router.get("/{codigo_publico}")
def get_order(codigo_publico: str, user: dict = Depends(get_current_user)) -> dict:
    with get_connection() as conn:
        order = conn.execute(
            """
            SELECT id_pedido, id_usuario
            FROM pedido
            WHERE codigo_publico = %s
            """,
            (codigo_publico,),
        ).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        if user["rol"] != "admin" and order["id_usuario"] != user["id_usuario"]:
            raise HTTPException(status_code=403, detail="No puedes ver este pedido.")
        return _format_order_detail(conn, codigo_publico)
