CREATE TABLE rol (
    id_rol SMALLSERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE usuario (
    id_usuario BIGSERIAL PRIMARY KEY,
    id_rol SMALLINT NOT NULL REFERENCES rol(id_rol),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sesion_usuario (
    id_sesion UUID PRIMARY KEY,
    id_usuario BIGINT NOT NULL REFERENCES usuario(id_usuario),
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    creada_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP NOT NULL,
    revocada_en TIMESTAMP
);

CREATE TABLE categoria (
    id_categoria BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    descripcion TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE proveedor (
    id_proveedor BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(150),
    email VARCHAR(255),
    telefono VARCHAR(30),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE producto (
    id_producto BIGSERIAL PRIMARY KEY,
    id_categoria BIGINT NOT NULL REFERENCES categoria(id_categoria),
    id_proveedor BIGINT REFERENCES proveedor(id_proveedor),
    sku VARCHAR(60) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio_unitario NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    stock_actual INTEGER NOT NULL CHECK (stock_actual >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pedido (
    id_pedido BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT REFERENCES usuario(id_usuario),
    codigo_publico VARCHAR(40) NOT NULL UNIQUE,
    nombre_cliente VARCHAR(150) NOT NULL,
    email_cliente VARCHAR(255) NOT NULL,
    telefono_cliente VARCHAR(30),
    tipo_entrega VARCHAR(20) NOT NULL CHECK (tipo_entrega IN ('delivery', 'pickup')),
    estado_pedido VARCHAR(30) NOT NULL,
    estado_pago VARCHAR(30) NOT NULL,
    nota_cliente TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmado_en TIMESTAMP
);

CREATE TABLE direccion_entrega (
    id_direccion_entrega BIGSERIAL PRIMARY KEY,
    id_pedido BIGINT NOT NULL UNIQUE REFERENCES pedido(id_pedido),
    linea_1 VARCHAR(255) NOT NULL,
    linea_2 VARCHAR(255),
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    referencia VARCHAR(255)
);

CREATE TABLE detalle_pedido (
    id_detalle_pedido BIGSERIAL PRIMARY KEY,
    id_pedido BIGINT NOT NULL REFERENCES pedido(id_pedido),
    id_producto BIGINT NOT NULL REFERENCES producto(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    UNIQUE (id_pedido, id_producto)
);

CREATE TABLE pago (
    id_pago BIGSERIAL PRIMARY KEY,
    id_pedido BIGINT NOT NULL UNIQUE REFERENCES pedido(id_pedido),
    metodo VARCHAR(20) NOT NULL CHECK (metodo IN ('cash', 'card', 'transfer')),
    monto NUMERIC(12,2) NOT NULL CHECK (monto >= 0),
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('pending', 'approved', 'rejected')),
    codigo_simulado VARCHAR(40) NOT NULL UNIQUE,
    procesado_en TIMESTAMP
);

CREATE TABLE historial_estado_pedido (
    id_historial BIGSERIAL PRIMARY KEY,
    id_pedido BIGINT NOT NULL REFERENCES pedido(id_pedido),
    id_usuario BIGINT REFERENCES usuario(id_usuario),
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    nota TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reabastecimiento (
    id_reabastecimiento BIGSERIAL PRIMARY KEY,
    id_proveedor BIGINT REFERENCES proveedor(id_proveedor),
    id_admin BIGINT NOT NULL REFERENCES usuario(id_usuario),
    nota TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalle_reabastecimiento (
    id_detalle_reab BIGSERIAL PRIMARY KEY,
    id_reabastecimiento BIGINT NOT NULL REFERENCES reabastecimiento(id_reabastecimiento),
    id_producto BIGINT NOT NULL REFERENCES producto(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    costo_unitario NUMERIC(12,2) NOT NULL CHECK (costo_unitario >= 0),
    UNIQUE (id_reabastecimiento, id_producto)
);

CREATE TABLE ajuste_inventario (
    id_ajuste BIGSERIAL PRIMARY KEY,
    id_producto BIGINT NOT NULL REFERENCES producto(id_producto),
    id_admin BIGINT NOT NULL REFERENCES usuario(id_usuario),
    cantidad_delta INTEGER NOT NULL,
    motivo TEXT NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_producto_categoria ON producto(id_categoria);
CREATE INDEX idx_producto_stock_actual ON producto(stock_actual);
CREATE INDEX idx_pedido_creado_en ON pedido(creado_en);
CREATE INDEX idx_pedido_usuario_creado ON pedido(id_usuario, creado_en);
CREATE INDEX idx_detalle_pedido_producto ON detalle_pedido(id_producto);
CREATE INDEX idx_pago_estado ON pago(estado);

CREATE VIEW vw_resumen_ventas AS
SELECT
    p.id_pedido,
    p.codigo_publico,
    p.creado_en,
    p.tipo_entrega,
    p.estado_pedido,
    p.estado_pago,
    COALESCE(SUM(dp.cantidad * dp.precio_unitario), 0) AS total_pedido
FROM pedido p
LEFT JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
GROUP BY
    p.id_pedido,
    p.codigo_publico,
    p.creado_en,
    p.tipo_entrega,
    p.estado_pedido,
    p.estado_pago;

