-- 003_security_roles.sql
-- Endurecimiento de permisos por rol bajo principio de minimo privilegio.
-- Se ejecuta despues de 001_schema.sql y 002_seed.sql.

BEGIN;

-- 1) Roles funcionales del sistema (NOLOGIN: usados para herencia a usuarios reales).
CREATE ROLE app_admin NOLOGIN;
CREATE ROLE app_inventory NOLOGIN;
CREATE ROLE app_sales NOLOGIN;
CREATE ROLE app_reporting NOLOGIN;
CREATE ROLE app_customer NOLOGIN;

-- 2) Cerrar acceso por defecto al esquema publico y reabrir solo a roles de aplicacion.
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_admin, app_inventory, app_sales, app_reporting, app_customer;

-- 3) Revocar acceso por defecto a objetos existentes para evitar privilegios heredados no deseados.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- 4) app_admin: acceso operativo total para mantenimiento y administracion integral.
-- Justificacion: rol de backoffice con responsabilidad completa sobre catalogo, cuentas y pedidos.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- 5) app_inventory: foco en catalogo e inventario, sin acceso a credenciales/sesiones/pagos.
-- Justificacion: separacion de funciones para evitar exposicion de datos sensibles.
GRANT SELECT ON categoria, proveedor, producto TO app_inventory;
GRANT INSERT, UPDATE ON categoria, proveedor, producto TO app_inventory;
GRANT SELECT, INSERT ON reabastecimiento, detalle_reabastecimiento, ajuste_inventario TO app_inventory;
GRANT SELECT ON pedido, detalle_pedido, historial_estado_pedido TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE categoria_id_categoria_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE proveedor_id_proveedor_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE producto_id_producto_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE reabastecimiento_id_reabastecimiento_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE detalle_reabastecimiento_id_detalle_reab_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE ajuste_inventario_id_ajuste_seq TO app_inventory;

-- Revocaciones explicitas de tablas sensibles para auditoria.
REVOKE ALL ON usuario, sesion_usuario, pago FROM app_inventory;

-- 6) app_sales: opera ciclo de pedido y cobro, con catalogo en solo lectura.
-- Justificacion: puede crear/actualizar pedidos y pagos sin administrar usuarios o inventario.
GRANT SELECT ON producto, categoria, proveedor TO app_sales;
GRANT SELECT, INSERT, UPDATE ON pedido, direccion_entrega, detalle_pedido, pago, historial_estado_pedido TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE pedido_id_pedido_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE direccion_entrega_id_direccion_entrega_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE detalle_pedido_id_detalle_pedido_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE pago_id_pago_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE historial_estado_pedido_id_historial_seq TO app_sales;

-- Revocaciones explicitas de tablas sensibles para limitar movimiento lateral.
REVOKE ALL ON usuario, sesion_usuario FROM app_sales;

-- 7) app_reporting: solo lectura para analitica y vista de resumen.
-- Justificacion: separa consumo BI/reportes de operaciones transaccionales.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reporting;
GRANT SELECT ON vw_resumen_ventas TO app_reporting;
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM app_reporting;

-- 8) app_customer: capacidades minimas para flujo de cliente autenticado.
-- Justificacion: puede registrar/actualizar su cuenta y registrar pedidos propios; sin acceso administrativo.
GRANT SELECT, INSERT, UPDATE ON usuario TO app_customer;
GRANT SELECT, INSERT, UPDATE, DELETE ON sesion_usuario TO app_customer;
GRANT SELECT ON categoria, producto TO app_customer;
GRANT SELECT, INSERT ON pedido, direccion_entrega, detalle_pedido, pago TO app_customer;
GRANT SELECT ON historial_estado_pedido, vw_resumen_ventas TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE usuario_id_usuario_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE pedido_id_pedido_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE direccion_entrega_id_direccion_entrega_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE detalle_pedido_id_detalle_pedido_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE pago_id_pago_seq TO app_customer;

-- Revocaciones explicitas para reforzar minimo privilegio en objetos administrativos.
REVOKE ALL ON rol, proveedor, reabastecimiento, detalle_reabastecimiento, ajuste_inventario FROM app_customer;

COMMIT;
