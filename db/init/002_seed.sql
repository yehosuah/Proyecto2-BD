TRUNCATE TABLE
    ajuste_inventario,
    detalle_reabastecimiento,
    reabastecimiento,
    historial_estado_pedido,
    pago,
    detalle_pedido,
    direccion_entrega,
    pedido,
    producto,
    proveedor,
    categoria,
    sesion_usuario,
    usuario,
    rol
RESTART IDENTITY CASCADE;

-- Credenciales demo:
-- admin@proyecto2.local / admin123
-- cliente@proyecto2.local / client123
-- inventario@proyecto2.local / inventario123
-- reportes@proyecto2.local / reportes123
-- catalogo@proyecto2.local / catalogo123
-- ventas@proyecto2.local / ventas123

INSERT INTO rol (nombre)
VALUES ('admin'), ('cliente'), ('inventario'), ('reportes'), ('catalogo'), ('ventas');

INSERT INTO usuario (
    id_rol,
    email,
    password_hash,
    nombre,
    apellido,
    telefono
)
VALUES
    -- Credenciales de demo:
    -- admin@proyecto2.local / admin123
    (
        (SELECT id_rol FROM rol WHERE nombre = 'admin'),
        'admin@proyecto2.local',
        'sha256:240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'Admin',
        'Demo',
        '5555-0001'
    ),
    -- cliente@proyecto2.local / cliente123
    (
        (SELECT id_rol FROM rol WHERE nombre = 'cliente'),
        'cliente@proyecto2.local',
        'sha256:09a31a7001e261ab1e056182a71d3cf57f582ca9a29cff5eb83be0f0549730a9',
        'Cliente',
        'Demo',
        '5555-0002'
    ),
    -- inventory@proyecto2.local / inventory123
    (
        (SELECT id_rol FROM rol WHERE nombre = 'inventory'),
        'inventory@proyecto2.local',
        'sha256:cd63ef271f9f5c81c3ac9e24e544f7e982360ebc027bf4e6b6960485b13f89e7',
        'Inventory',
        'Demo',
        '5555-0003'
    ),
    -- sales@proyecto2.local / sales123
    (
        (SELECT id_rol FROM rol WHERE nombre = 'sales'),
        'sales@proyecto2.local',
        'sha256:6bc0a63cb29c92306020c0a6bbc358cc4628db277dc06e253535e126517ad637',
        'Sales',
        'Demo',
        '5555-0004'
    ),
    -- support@proyecto2.local / support123
    (
        (SELECT id_rol FROM rol WHERE nombre = 'support'),
        'support@proyecto2.local',
        'sha256:a67d22cef2f6639d71b8901b5b2bbee4a2400d92c70e60c179c0fd76d72d6c23',
        'Support',
        'Demo',
        '5555-0005'
    );


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
        (SELECT id_rol FROM rol WHERE nombre = 'inventario'),
        'inventario@proyecto2.local',
        'sha256:f54568eeb40e6872d8df7afffc13608decaee72e20803a0da71309ece6cc73ea',
        'Inventario',
        'Demo',
        '5555-0003'
    ),
    (
        (SELECT id_rol FROM rol WHERE nombre = 'reportes'),
        'reportes@proyecto2.local',
        'sha256:baa1e8c9e7a3650b5ab6b0c2b91c2f11c17ed96e67b27fb82c74d90a70a6981a',
        'Reportes',
        'Demo',
        '5555-0004'
    ),
    (
        (SELECT id_rol FROM rol WHERE nombre = 'catalogo'),
        'catalogo@proyecto2.local',
        'sha256:2d5fd144b14cd00bdeb7701fce0819c7412a0bf99044df4f77a5fcf64f9c105e',
        'Catalogo',
        'Demo',
        '5555-0005'
    ),
    (
        (SELECT id_rol FROM rol WHERE nombre = 'ventas'),
        'ventas@proyecto2.local',
        'sha256:e2151232843fc5ee75d0c8bfc0c74bdcdace97b001a7dab658f7a27ecc8d93f5',
        'Ventas',
        'Demo',
        '5555-0006'
    );

INSERT INTO usuario (
    id_rol,
    email,
    password_hash,
    nombre,
    apellido,
    telefono
)
SELECT
    (SELECT id_rol FROM rol WHERE nombre = 'cliente'),
    format('cliente%02s@proyecto2.local', gs),
    'sha256:186474c1f2c2f735a54c2cf82ee8e87f2a5cd30940e280029363fecedfc5328c',
    format('Cliente%02s', gs),
    format('Prueba%02s', gs),
    format('5555-%04s', 2000 + gs)
FROM generate_series(1, 28) AS gs;

INSERT INTO sesion_usuario (
    id_sesion,
    id_usuario,
    token_hash,
    creada_en,
    expira_en
)
SELECT
    md5(format('session-id-%s', gs))::uuid,
    2 + gs,
    md5(format('session-token-%s', gs)),
    CURRENT_TIMESTAMP - make_interval(days => gs % 3),
    CURRENT_TIMESTAMP + make_interval(days => 10 + gs)
FROM generate_series(1, 25) AS gs;

INSERT INTO categoria (nombre, descripcion)
VALUES
    ('Hogar', 'Objetos para ambientar espacios del hogar'),
    ('Cocina', 'Utensilios y articulos funcionales para cocina'),
    ('Decoracion', 'Piezas decorativas para espacios interiores'),
    ('Baño', 'Cuidado y organizacion de baño'),
    ('Textiles', 'Mantas, toallas y textiles suaves'),
    ('Bienestar', 'Productos para relajacion y autocuidado'),
    ('Accesorios', 'Accesorios generales de tienda');

INSERT INTO categoria (nombre, descripcion)
VALUES
    ('Organizacion', 'Cajas, bolsas y contenedores para ordenar espacios'),
    ('Plantas', 'Macetas, soportes y articulos para plantas de interior'),
    ('Iluminacion', 'Lamparas, portavelas y accesorios de luz ambiental'),
    ('Mesa', 'Piezas para servir y montar mesa'),
    ('Limpieza', 'Articulos reutilizables para limpieza diaria'),
    ('Papeleria', 'Cuadernos y articulos de escritorio'),
    ('Dormitorio', 'Piezas suaves y practicas para dormitorio'),
    ('Jardin', 'Accesorios pequenos para balcon o jardin'),
    ('Cuidado personal', 'Productos de cuidado personal sin formulacion medica'),
    ('Aromas', 'Difusores, aceites y fragancias ambientales'),
    ('Ceramica', 'Piezas de ceramica artesanal y utilitaria'),
    ('Madera', 'Objetos pequenos fabricados en madera'),
    ('Vidrio', 'Contenedores y piezas decorativas de vidrio'),
    ('Regalos', 'Productos preparados para regalo'),
    ('Temporada', 'Articulos rotativos por epoca'),
    ('Mascotas', 'Accesorios sencillos para mascotas de casa'),
    ('Viaje', 'Organizadores y bolsas para viaje'),
    ('Oficina', 'Accesorios de escritorio y trabajo en casa');

INSERT INTO proveedor (nombre, contacto, email, telefono)
VALUES
    ('Taller Arcilla Viva', 'Laura Diaz', 'laura@arcillaviva.gt', '2222-1001'),
    ('Textiles del Valle', 'Pablo Leon', 'pablo@textilesvalle.gt', '2222-1002'),
    ('Aromas Natura', 'Elena Ruiz', 'elena@aromasnatura.gt', '2222-1003'),
    ('Casa Serena Supply', 'Mario Perez', 'mario@casaserena.gt', '2222-1004'),
    ('Botanica Urbana', 'Ana Torres', 'ana@botanicaurbana.gt', '2222-1005');

INSERT INTO proveedor (nombre, contacto, email, telefono)
VALUES
    ('Organiza Studio', 'Sofia Mendez', 'sofia@organizastudio.gt', '2233-1006'),
    ('Luz de Patio', 'Ricardo Molina', 'ricardo@luzdepatio.gt', '2233-1007'),
    ('Mesa Clara', 'Gabriela Soto', 'gabriela@mesaclara.gt', '2233-1008'),
    ('Eco Limpio Local', 'Daniel Chacon', 'daniel@ecolimpiolocal.gt', '2233-1009'),
    ('Papel Nativo', 'Mariana Lopez', 'mariana@papelnativo.gt', '2233-1010'),
    ('Dormir Suave', 'Alejandro Cano', 'alejandro@dormirsuave.gt', '2233-1011'),
    ('Verde Balcon', 'Lucia Reyes', 'lucia@verdebalcon.gt', '2233-1012'),
    ('Cuidado Simple', 'Paola Estrada', 'paola@cuidadosimple.gt', '2233-1013'),
    ('Bruma Aromas', 'Nicolas Herrera', 'nicolas@brumaaromas.gt', '2233-1014'),
    ('Ceramica Norte', 'Andrea Pineda', 'andrea@ceramicanorte.gt', '2233-1015'),
    ('Madera Fina GT', 'Hector Salazar', 'hector@maderafinagt.gt', '2233-1016'),
    ('Vidrio Claro', 'Julia Morales', 'julia@vidrioclaro.gt', '2233-1017'),
    ('Detalle Listo', 'Monica Fuentes', 'monica@detallelisto.gt', '2233-1018'),
    ('Temporada Casa', 'Oscar Vargas', 'oscar@temporadacasa.gt', '2233-1019'),
    ('Patitas Casa', 'Carla Rivas', 'carla@patitascasa.gt', '2233-1020'),
    ('Ruta Ordenada', 'Diego Aguilar', 'diego@rutaordenada.gt', '2233-1021'),
    ('Oficina Serena', 'Ines Barrios', 'ines@oficinaserena.gt', '2233-1022'),
    ('Algodon Central', 'Mateo Cifuentes', 'mateo@algodoncentral.gt', '2233-1023'),
    ('Bazar Interior', 'Valeria Cruz', 'valeria@bazarinterior.gt', '2233-1024'),
    ('Linea Natural', 'Esteban Ramos', 'esteban@lineanatural.gt', '2233-1025');

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
    (1, 5, 'HOG-001', 'Maceta de ceramica', 'Maceta clara para interior', 158.00, 12),
    (1, 5, 'HOG-002', 'Canasto tejido', 'Canasto natural con asas', 206.00, 8),
    (2, 1, 'COC-001', 'Taza ceramica', 'Taza artesanal para cafe', 125.00, 18),
    (2, 1, 'COC-002', 'Olla esmaltada', 'Olla compacta para cocina diaria', 242.00, 11),
    (3, 1, 'DEC-001', 'Vaso florero arena', 'Florero neutro de una sola pieza', 179.00, 9),
    (4, 3, 'BAN-001', 'Dispensador ambar', 'Dispensador recargable de bano', 189.00, 14),
    (4, 3, 'BAN-002', 'Jabon liquido avena', 'Jabon liquido suave para manos', 98.00, 5),
    (5, 2, 'TEX-001', 'Manta de algodon', 'Manta suave de textura liviana', 249.00, 7),
    (5, 2, 'TEX-002', 'Toalla premium', 'Toalla gruesa para uso diario', 139.00, 16),
    (6, 3, 'BIE-001', 'Vela aromatica', 'Vela de lavanda para relajacion', 137.00, 6),
    (6, 3, 'BIE-002', 'Aceite corporal almendra', 'Aceite corporal hidratante', 175.00, 4),
    (7, 4, 'ACC-001', 'Bolsa organizadora', 'Bolsa de tela para accesorios', 118.00, 20);

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
    (8, 6, 'ORG-001', 'Caja plegable lino', 'Caja organizadora de tela con estructura firme', 132.00, 15),
    (9, 5, 'PLA-001', 'Soporte para maceta', 'Base elevada para macetas pequenas de interior', 119.00, 13),
    (10, 7, 'ILU-001', 'Portavela bajo', 'Portavela ceramico para luz ambiental', 92.00, 9),
    (11, 8, 'MES-001', 'Bandeja ovalada', 'Bandeja de servicio en tono neutro', 165.00, 12),
    (12, 9, 'LIM-001', 'Cepillo de madera', 'Cepillo reutilizable para limpieza de cocina', 68.00, 11),
    (12, 9, 'LIM-002', 'Panitos de algodon', 'Set de panitos lavables para limpieza diaria', 89.00, 7),
    (13, 10, 'PAP-001', 'Cuaderno kraft', 'Cuaderno de tapa kraft para notas diarias', 58.00, 20),
    (13, 10, 'PAP-002', 'Planificador semanal', 'Planificador simple para escritorio', 82.00, 14),
    (14, 11, 'DOR-001', 'Funda decorativa', 'Funda de cojin en algodon tejido', 126.00, 8),
    (14, 23, 'DOR-002', 'Cojin lumbar', 'Cojin rectangular para cama o sillon', 158.00, 6),
    (15, 12, 'JAR-001', 'Pala de jardin pequena', 'Herramienta compacta para macetas y balcon', 72.00, 16),
    (15, 12, 'JAR-002', 'Etiquetas para plantas', 'Set de etiquetas reutilizables para macetas', 49.00, 21),
    (16, 13, 'CUI-001', 'Cepillo corporal seco', 'Cepillo de cerdas naturales para cuidado personal', 116.00, 5),
    (16, 13, 'CUI-002', 'Esponja vegetal', 'Esponja vegetal para rutina de bano', 45.00, 17),
    (17, 14, 'ARO-001', 'Difusor de varillas', 'Difusor ambiental con aroma suave', 148.00, 9),
    (18, 15, 'CER-001', 'Plato de ceramica', 'Plato artesanal de borde irregular', 134.00, 13),
    (19, 16, 'MAD-001', 'Tabla pequena', 'Tabla de madera para servir o decorar', 156.00, 10),
    (20, 17, 'VID-001', 'Frasco de vidrio', 'Frasco transparente con tapa para organizacion', 64.00, 19),
    (21, 18, 'REG-001', 'Caja de regalo natural', 'Caja armable para preparar regalos pequenos', 52.00, 22),
    (22, 19, 'TEM-001', 'Guirnalda de temporada', 'Guirnalda sencilla para decorar estantes', 96.00, 8),
    (23, 20, 'MAS-001', 'Tapete para mascota', 'Tapete lavable pequeno para area de descanso', 142.00, 9),
    (24, 21, 'VIA-001', 'Neceser de tela', 'Neceser compacto para viaje y organizacion', 104.00, 15),
    (25, 22, 'OFI-001', 'Organizador de escritorio', 'Base de escritorio para lapices y notas', 118.00, 12);

INSERT INTO reabastecimiento (
    id_proveedor,
    id_admin,
    nota,
    creado_en
)
SELECT
    ((gs - 1) % 25) + 1,
    1,
    format('Ingreso de inventario %02s', gs),
    TIMESTAMP '2025-04-01 08:00:00' + make_interval(days => gs)
FROM generate_series(1, 25) AS gs;

INSERT INTO detalle_reabastecimiento (
    id_reabastecimiento,
    id_producto,
    cantidad,
    costo_unitario
)
SELECT
    r.id_reabastecimiento,
    ((r.id_reabastecimiento + offs) % 35) + 1,
    6 + offs,
    (25 + r.id_reabastecimiento + offs * 3)::numeric(12,2)
FROM reabastecimiento r
CROSS JOIN generate_series(0, 1) AS offs;

INSERT INTO ajuste_inventario (
    id_producto,
    id_admin,
    cantidad_delta,
    motivo,
    creado_en
)
SELECT
    ((gs + 6) % 35) + 1,
    1,
    CASE WHEN gs % 2 = 0 THEN 2 ELSE -1 END,
    format('Ajuste operativo %02s', gs),
    TIMESTAMP '2025-04-05 09:00:00' + make_interval(days => gs)
FROM generate_series(1, 25) AS gs;

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
    creado_en,
    confirmado_en
)
SELECT
    CASE WHEN gs % 4 = 0 THEN NULL ELSE ((gs - 1) % 20) + 2 END,
    format('ORD-SEED-%03s', gs),
    format('Cliente Pedido %02s', gs),
    format('pedido%02s@proyecto2.local', gs),
    format('5599-%04s', 1000 + gs),
    CASE WHEN gs % 3 = 0 THEN 'delivery' ELSE 'pickup' END,
    CASE
        WHEN gs % 7 = 0 THEN 'cancelado'
        WHEN gs % 3 = 0 THEN 'en_preparacion'
        ELSE 'listo_para_retiro'
    END,
    CASE WHEN gs % 7 = 0 THEN 'rechazado' ELSE 'aprobado' END,
    format('Pedido sembrado %02s', gs),
    TIMESTAMP '2025-05-01 09:00:00' + make_interval(hours => gs * 5),
    TIMESTAMP '2025-05-01 09:20:00' + make_interval(hours => gs * 5)
FROM generate_series(1, 30) AS gs;

INSERT INTO direccion_entrega (
    id_pedido,
    linea_1,
    linea_2,
    ciudad,
    departamento,
    referencia
)
SELECT
    id_pedido,
    format('Zona %s Avenida %s', (id_pedido % 15) + 1, (id_pedido % 6) + 1),
    format('Casa %s', 100 + id_pedido),
    'Ciudad de Guatemala',
    'Guatemala',
    format('Referencia entrega %s', id_pedido)
FROM pedido
WHERE tipo_entrega = 'delivery';

INSERT INTO detalle_pedido (
    id_pedido,
    id_producto,
    cantidad,
    precio_unitario
)
SELECT
    p.id_pedido,
    ((p.id_pedido + offs) % 35) + 1,
    CASE WHEN offs = 0 THEN 1 + (p.id_pedido % 2) ELSE 1 END,
    pr.precio_unitario
FROM pedido p
CROSS JOIN generate_series(0, 1) AS offs
JOIN producto pr ON pr.id_producto = ((p.id_pedido + offs) % 35) + 1;

INSERT INTO pago (
    id_pedido,
    metodo,
    monto,
    estado,
    codigo_simulado,
    procesado_en
)
SELECT
    p.id_pedido,
    CASE
        WHEN p.id_pedido % 3 = 0 THEN 'transferencia'
        WHEN p.id_pedido % 2 = 0 THEN 'tarjeta'
        ELSE 'efectivo'
    END,
    totals.total_pedido,
    CASE WHEN p.estado_pago = 'rechazado' THEN 'rechazado' ELSE 'aprobado' END,
    format('PAY-SEED-%03s', p.id_pedido),
    p.confirmado_en
FROM pedido p
JOIN (
    SELECT
        id_pedido,
        SUM(cantidad * precio_unitario) AS total_pedido
    FROM detalle_pedido
    GROUP BY id_pedido
) AS totals ON totals.id_pedido = p.id_pedido;

INSERT INTO historial_estado_pedido (
    id_pedido,
    id_usuario,
    estado_anterior,
    estado_nuevo,
    nota,
    creado_en
)
SELECT
    p.id_pedido,
    COALESCE(p.id_usuario, 1),
    NULL,
    'creado',
    'Pedido registrado en el sistema.',
    p.creado_en
FROM pedido p;

INSERT INTO historial_estado_pedido (
    id_pedido,
    id_usuario,
    estado_anterior,
    estado_nuevo,
    nota,
    creado_en
)
SELECT
    p.id_pedido,
    1,
    'creado',
    p.estado_pedido,
    CASE
        WHEN p.estado_pedido = 'cancelado' THEN 'Pago rechazado en simulacion.'
        ELSE 'Estado actualizado automaticamente tras aprobacion.'
    END,
    p.confirmado_en
FROM pedido p;
