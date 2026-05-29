-- 003_security_roles.sql
-- Roles PostgreSQL del Proyecto 3. Se crean exactamente cinco roles DBMS
-- de aplicacion y se asignan permisos bajo minimo privilegio.

BEGIN;

CREATE ROLE app_admin NOLOGIN;
CREATE ROLE app_inventory NOLOGIN;
CREATE ROLE app_sales NOLOGIN;
CREATE ROLE app_reporting NOLOGIN;
CREATE ROLE app_customer NOLOGIN;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO
    app_admin,
    app_inventory,
    app_sales,
    app_reporting,
    app_customer;

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- El usuario real de conexion lo define Docker con POSTGRES_USER.
-- Se le hereda app_admin sin crear usuarios DBMS extra en este script.
GRANT app_admin TO CURRENT_USER;

-- Admin: control operativo completo sobre datos, secuencias y reportes.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- Inventario: administra catalogo fisico, proveedores, stock y entradas.
GRANT SELECT ON categoria, proveedor, producto TO app_inventory;
GRANT INSERT, UPDATE ON categoria, proveedor, producto TO app_inventory;
GRANT SELECT, INSERT, UPDATE ON reabastecimiento, detalle_reabastecimiento, ajuste_inventario TO app_inventory;
GRANT SELECT ON pedido, detalle_pedido, historial_estado_pedido TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE categoria_id_categoria_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE proveedor_id_proveedor_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE producto_id_producto_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE reabastecimiento_id_reabastecimiento_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE detalle_reabastecimiento_id_detalle_reab_seq TO app_inventory;
GRANT USAGE, SELECT ON SEQUENCE ajuste_inventario_id_ajuste_seq TO app_inventory;
REVOKE ALL ON rol, usuario, sesion_usuario, pago FROM app_inventory;

-- Ventas: consulta catalogo y administra pedidos, pagos e historial comercial.
GRANT SELECT ON categoria, proveedor, producto TO app_sales;
GRANT SELECT, INSERT, UPDATE ON pedido, direccion_entrega, detalle_pedido, pago, historial_estado_pedido TO app_sales;
GRANT SELECT ON vw_resumen_ventas TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE pedido_id_pedido_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE direccion_entrega_id_direccion_entrega_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE detalle_pedido_id_detalle_pedido_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE pago_id_pago_seq TO app_sales;
GRANT USAGE, SELECT ON SEQUENCE historial_estado_pedido_id_historial_seq TO app_sales;
REVOKE ALL ON rol, usuario, sesion_usuario, reabastecimiento, detalle_reabastecimiento, ajuste_inventario FROM app_sales;

-- Reportes: solo lectura, sin mutacion de tablas o secuencias.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reporting;
GRANT SELECT ON vw_resumen_ventas TO app_reporting;
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM app_reporting;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM app_reporting;

-- Cliente: autenticacion, sesion, lectura de catalogo y creacion de pedidos propios.
GRANT SELECT, INSERT, UPDATE ON usuario TO app_customer;
GRANT SELECT, INSERT, UPDATE, DELETE ON sesion_usuario TO app_customer;
GRANT SELECT ON categoria, producto, vw_resumen_ventas TO app_customer;
GRANT SELECT, INSERT ON pedido, direccion_entrega, detalle_pedido, pago TO app_customer;
GRANT SELECT ON historial_estado_pedido TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE usuario_id_usuario_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE pedido_id_pedido_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE direccion_entrega_id_direccion_entrega_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE detalle_pedido_id_detalle_pedido_seq TO app_customer;
GRANT USAGE, SELECT ON SEQUENCE pago_id_pago_seq TO app_customer;
REVOKE ALL ON rol, proveedor, reabastecimiento, detalle_reabastecimiento, ajuste_inventario FROM app_customer;

COMMIT;
