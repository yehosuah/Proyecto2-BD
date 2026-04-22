from datetime import date
from io import StringIO
import csv


def build_sales_report_query() -> str:
    return """
        WITH filtered_sales AS (
            SELECT
                p.id_pedido,
                p.codigo_publico,
                DATE(p.creado_en) AS fecha,
                p.estado_pedido,
                p.estado_pago,
                p.tipo_entrega,
                COALESCE(c.nombre, 'Invitado') AS cliente,
                COALESCE(v.total_pedido, 0) AS total_pedido
            FROM pedido p
            JOIN vw_resumen_ventas v ON v.id_pedido = p.id_pedido
            LEFT JOIN usuario c ON c.id_usuario = p.id_usuario
            WHERE (%(start_date)s::date IS NULL OR DATE(p.creado_en) >= %(start_date)s::date)
              AND (%(end_date)s::date IS NULL OR DATE(p.creado_en) <= %(end_date)s::date)
              AND (%(status)s::text IS NULL OR p.estado_pedido = %(status)s::text)
        ),
        daily_totals AS (
            SELECT
                fecha,
                COUNT(*) AS ordenes,
                SUM(total_pedido) AS ventas_totales
            FROM filtered_sales
            GROUP BY fecha
            HAVING SUM(total_pedido) > 0
        )
        SELECT fecha, ordenes, ventas_totales
        FROM daily_totals
        ORDER BY fecha ASC
    """


def export_rows_to_csv(rows: list[dict], headers: list[str]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def normalize_date_range(start_date: str | None, end_date: str | None) -> dict[str, str | None]:
    return {"start_date": start_date, "end_date": end_date}
