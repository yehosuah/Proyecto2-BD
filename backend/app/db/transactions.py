SERIALIZABLE = "SERIALIZABLE"


def serializable_checkout_statements() -> list[str]:
    return [
        "BEGIN",
        f"SET TRANSACTION ISOLATION LEVEL {SERIALIZABLE}",
        "-- Lock cart products with SELECT ... FOR UPDATE",
        "-- Insert pedido, detalle_pedido, pago",
        "-- Update producto.stock_actual",
        "COMMIT",
    ]

