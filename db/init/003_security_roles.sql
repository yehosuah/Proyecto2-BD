-- 003_security_roles.sql
-- Modelo de seguridad DBMS para PostgreSQL

BEGIN;

-- Roles sin login (grupos de permisos)
CREATE ROLE app_admin NOLOGIN;
CREATE ROLE app_cliente NOLOGIN;
CREATE ROLE app_invitado NOLOGIN;

-- Endurecimiento inicial
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- Permisos base para ejecutar consultas dentro del esquema
GRANT USAGE ON SCHEMA public TO app_admin, app_cliente, app_invitado;

-- =========================
-- app_admin: control total operativo
-- =========================
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- =========================
-- app_cliente: operaciones de cliente autenticado
-- =========================
GRANT SELECT ON rol, categoria, proveedor, producto TO app_cliente;

GRANT SELECT ON usuario TO app_cliente;
REVOKE SELECT(password_hash) ON usuario FROM app_cliente;

GRANT SELECT, INSERT, UPDATE ON sesion_usuario TO app_cliente;
GRANT SELECT, INSERT ON pedido, direccion_entrega, detalle_pedido, pago TO app_cliente;
GRANT SELECT ON historial_estado_pedido TO app_cliente;

-- Reportes de lectura para cliente autenticado
GRANT SELECT ON vw_resumen_ventas TO app_cliente;

-- =========================
-- app_invitado: solo catalogo/checkout minimo
-- =========================
GRANT SELECT ON categoria, producto TO app_invitado;
GRANT INSERT ON pedido, direccion_entrega, detalle_pedido, pago TO app_invitado;
GRANT SELECT ON vw_resumen_ventas TO app_invitado;

-- Seguridad adicional explicita
REVOKE UPDATE, DELETE ON pedido, direccion_entrega, detalle_pedido, pago FROM app_invitado;
REVOKE INSERT, UPDATE, DELETE ON producto FROM app_cliente, app_invitado;

-- Permisos por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_admin;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO app_admin;

COMMIT;
