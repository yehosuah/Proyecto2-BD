-- 004_stored_procedures.sql
-- Stored procedures criticos del Proyecto 3. Este archivo corre despues de
-- 003_security_roles.sql para poder otorgar EXECUTE sobre rutinas existentes.

BEGIN;

CREATE OR REPLACE PROCEDURE sp_create_category(
    IN p_nombre text,
    IN p_descripcion text,
    IN p_activa boolean,
    OUT o_id_categoria bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO categoria (nombre, descripcion, activa)
    VALUES (p_nombre, p_descripcion, COALESCE(p_activa, TRUE))
    RETURNING id_categoria INTO o_id_categoria;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_update_category(
    IN p_id_categoria bigint,
    IN p_nombre text,
    IN p_descripcion text,
    IN p_activa boolean,
    OUT o_found boolean
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows bigint;
BEGIN
    UPDATE categoria
    SET nombre = p_nombre,
        descripcion = p_descripcion,
        activa = COALESCE(p_activa, TRUE)
    WHERE id_categoria = p_id_categoria;

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    o_found := v_rows > 0;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_create_product(
    IN p_id_categoria bigint,
    IN p_id_proveedor bigint,
    IN p_sku text,
    IN p_nombre text,
    IN p_descripcion text,
    IN p_precio_unitario numeric,
    IN p_stock_actual integer,
    IN p_activo boolean,
    OUT o_id_producto bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
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
    VALUES (
        p_id_categoria,
        p_id_proveedor,
        p_sku,
        p_nombre,
        p_descripcion,
        p_precio_unitario,
        p_stock_actual,
        COALESCE(p_activo, TRUE)
    )
    RETURNING id_producto INTO o_id_producto;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_update_product(
    IN p_id_producto bigint,
    IN p_id_categoria bigint,
    IN p_id_proveedor bigint,
    IN p_sku text,
    IN p_nombre text,
    IN p_descripcion text,
    IN p_precio_unitario numeric,
    IN p_stock_actual integer,
    IN p_activo boolean,
    OUT o_found boolean
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows bigint;
BEGIN
    UPDATE producto
    SET id_categoria = p_id_categoria,
        id_proveedor = p_id_proveedor,
        sku = p_sku,
        nombre = p_nombre,
        descripcion = p_descripcion,
        precio_unitario = p_precio_unitario,
        stock_actual = p_stock_actual,
        activo = COALESCE(p_activo, TRUE),
        actualizado_en = CURRENT_TIMESTAMP
    WHERE id_producto = p_id_producto;

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    o_found := v_rows > 0;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_update_sale_status(
    IN p_codigo_publico text,
    IN p_estado_pedido text,
    IN p_id_admin bigint,
    OUT o_id_pedido bigint,
    OUT o_found boolean
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado_anterior text;
BEGIN
    SELECT id_pedido, estado_pedido
    INTO o_id_pedido, v_estado_anterior
    FROM pedido
    WHERE codigo_publico = p_codigo_publico
    FOR UPDATE;

    IF NOT FOUND THEN
        o_id_pedido := NULL;
        o_found := FALSE;
        RETURN;
    END IF;

    UPDATE pedido
    SET estado_pedido = p_estado_pedido
    WHERE id_pedido = o_id_pedido;

    INSERT INTO historial_estado_pedido (
        id_pedido,
        id_usuario,
        estado_anterior,
        estado_nuevo,
        nota
    )
    VALUES (
        o_id_pedido,
        p_id_admin,
        v_estado_anterior,
        p_estado_pedido,
        'Cambio manual desde stored procedure.'
    );

    o_found := TRUE;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_apply_inventory_adjustment(
    IN p_id_producto bigint,
    IN p_id_admin bigint,
    IN p_cantidad_delta integer,
    IN p_motivo text,
    OUT o_id_ajuste bigint,
    OUT o_stock_actual integer
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_actual integer;
BEGIN
    o_id_ajuste := NULL;
    o_stock_actual := NULL;

    BEGIN
        SELECT stock_actual
        INTO v_stock_actual
        FROM producto
        WHERE id_producto = p_id_producto
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Producto no encontrado.'
                USING ERRCODE = 'P0002';
        END IF;

        IF v_stock_actual + p_cantidad_delta < 0 THEN
            RAISE EXCEPTION 'El ajuste dejaria stock negativo.'
                USING ERRCODE = '23514';
        END IF;

        UPDATE producto
        SET stock_actual = stock_actual + p_cantidad_delta,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id_producto = p_id_producto
        RETURNING stock_actual INTO o_stock_actual;

        INSERT INTO ajuste_inventario (
            id_producto,
            id_admin,
            cantidad_delta,
            motivo
        )
        VALUES (
            p_id_producto,
            p_id_admin,
            p_cantidad_delta,
            p_motivo
        )
        RETURNING id_ajuste INTO o_id_ajuste;
    EXCEPTION WHEN OTHERS THEN
        -- En PostgreSQL el bloque EXCEPTION funciona como subtransaccion:
        -- revierte lo ejecutado dentro del bloque y devuelve indicadores nulos.
        o_id_ajuste := NULL;
        o_stock_actual := NULL;
    END;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_create_restock(
    IN p_id_proveedor bigint,
    IN p_id_admin bigint,
    IN p_nota text,
    OUT o_id_reabastecimiento bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO reabastecimiento (
        id_proveedor,
        id_admin,
        nota
    )
    VALUES (
        p_id_proveedor,
        p_id_admin,
        p_nota
    )
    RETURNING id_reabastecimiento INTO o_id_reabastecimiento;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_add_restock_detail(
    IN p_id_reabastecimiento bigint,
    IN p_id_producto bigint,
    IN p_cantidad integer,
    IN p_costo_unitario numeric,
    OUT o_id_detalle_reab bigint,
    OUT o_stock_actual integer
)
LANGUAGE plpgsql
AS $$
BEGIN
    o_id_detalle_reab := NULL;
    o_stock_actual := NULL;

    BEGIN
        IF p_cantidad <= 0 THEN
            RAISE EXCEPTION 'La cantidad de reabastecimiento debe ser positiva.'
                USING ERRCODE = '23514';
        END IF;

        INSERT INTO detalle_reabastecimiento (
            id_reabastecimiento,
            id_producto,
            cantidad,
            costo_unitario
        )
        VALUES (
            p_id_reabastecimiento,
            p_id_producto,
            p_cantidad,
            p_costo_unitario
        )
        RETURNING id_detalle_reab INTO o_id_detalle_reab;

        UPDATE producto
        SET stock_actual = stock_actual + p_cantidad,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id_producto = p_id_producto
        RETURNING stock_actual INTO o_stock_actual;

        IF o_stock_actual IS NULL THEN
            RAISE EXCEPTION 'Producto no encontrado.'
                USING ERRCODE = 'P0002';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        -- Misma estrategia segura: subtransaccion revertida y senal de fallo.
        o_id_detalle_reab := NULL;
        o_stock_actual := NULL;
    END;
END;
$$;

REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;

GRANT EXECUTE ON PROCEDURE sp_create_category(text, text, boolean) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_update_category(bigint, text, text, boolean) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_create_product(bigint, bigint, text, text, text, numeric, integer, boolean) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_update_product(bigint, bigint, bigint, text, text, text, numeric, integer, boolean) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_update_sale_status(text, text, bigint) TO app_admin, app_sales;
GRANT EXECUTE ON PROCEDURE sp_apply_inventory_adjustment(bigint, bigint, integer, text) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_create_restock(bigint, bigint, text) TO app_admin, app_inventory;
GRANT EXECUTE ON PROCEDURE sp_add_restock_detail(bigint, bigint, integer, numeric) TO app_admin, app_inventory;

COMMIT;
