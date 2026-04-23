INSERT INTO rol (nombre)
VALUES ('admin'), ('cliente');

INSERT INTO usuario (
    id_rol,
    email,
    password_hash,
    nombre,
    apellido,
    telefono
)
VALUES
    (
        (SELECT id_rol FROM rol WHERE nombre = 'admin'),
        'admin@proyecto2.local',
        'sha256:240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'Admin',
        'Demo',
        '5555-0001'
    ),
    (
        (SELECT id_rol FROM rol WHERE nombre = 'cliente'),
        'cliente@proyecto2.local',
        'sha256:186474c1f2c2f735a54c2cf82ee8e87f2a5cd30940e280029363fecedfc5328c',
        'Cliente',
        'Demo',
        '5555-0002'
    );

INSERT INTO categoria (nombre, descripcion)
VALUES
    ('Accesorios', 'Accesorios generales de tienda'),
    ('Papeleria', 'Productos de papeleria y oficina'),
    ('Tecnologia', 'Productos basicos de tecnologia');

INSERT INTO proveedor (nombre, contacto, email, telefono)
VALUES
    ('Distribuidora Central', 'Laura Diaz', 'laura@distribuidora.gt', '2222-1000'),
    ('Suministros Urbanos', 'Carlos Ruiz', 'carlos@suministros.gt', '2222-2000');

INSERT INTO producto (
    id_categoria,
    id_proveedor,
    sku,
    nombre,
    descripcion,
    precio_unitario,
    stock_actual
)
VALUES
    (
        (SELECT id_categoria FROM categoria WHERE nombre = 'Accesorios'),
        (SELECT id_proveedor FROM proveedor WHERE nombre = 'Distribuidora Central'),
        'ACC-001',
        'Mochila Basica',
        'Mochila para uso diario',
        149.99,
        20
    ),
    (
        (SELECT id_categoria FROM categoria WHERE nombre = 'Papeleria'),
        (SELECT id_proveedor FROM proveedor WHERE nombre = 'Suministros Urbanos'),
        'PAP-001',
        'Cuaderno Profesional',
        'Cuaderno de 100 hojas',
        24.50,
        50
    ),
    (
        (SELECT id_categoria FROM categoria WHERE nombre = 'Tecnologia'),
        (SELECT id_proveedor FROM proveedor WHERE nombre = 'Distribuidora Central'),
        'TEC-001',
        'Mouse Inalambrico',
        'Mouse ergonomico de uso general',
        89.00,
        15
    );
