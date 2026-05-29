# Diseno de Base de Datos

## 1. Proposito del documento

Este documento presenta el diseno de base de datos del proyecto. Incluye:

- el modelo conceptual;
- el modelo relacional;
- la justificacion de normalizacion hasta 3FN;
- la relacion entre el diseno y el DDL ejecutable;
- la estrategia de indices;
- el estado y la estrategia del script de datos de prueba.

La parte ejecutable del diseno esta en estos archivos:

- `db/init/001_schema.sql`: DDL fisico, indices y `VIEW`.
- `db/init/002_seed.sql`: datos de arranque y base para las semillas de prueba.

## 2. Alcance y decisiones de negocio

Este diseno usa las siguientes decisiones de negocio:

- Frontend en Vue con tienda publica, area de cuenta cliente y panel administrativo.
- Backend en FastAPI usando SQLAlchemy ORM para CRUD y SQL explicito para reportes avanzados cuando conviene.
- PostgreSQL como DBMS.
- Pago simulado interno, sin integracion con pasarelas reales.
- Soporte para `delivery` y `pickup`.
- Compras permitidas sin crear cuenta.
- Usuarios registrados con perfil e historial de pedidos.
- Administrador autenticado con acceso al panel administrativo.
- Productos simples de un solo SKU.
- Reabastecimiento simple y ajustes directos de stock.

La meta del modelo es priorizar claridad academica, trazabilidad de reglas de negocio y soporte para la parte SQL/transaccional del proyecto.

## 3. Entidades principales

- `rol`: define los tipos de usuario del sistema (`admin`, `inventario`, `ventas`, `reportes`, `cliente`).
- `usuario`: almacena cuentas autenticadas.
- `sesion_usuario`: conserva sesiones de login/logout.
- `categoria`: clasifica productos del catalogo.
- `proveedor`: registra origen de abastecimiento.
- `producto`: representa el SKU vendible y su stock actual.
- `pedido`: encabezado de cada compra, hecha por invitado o usuario registrado.
- `direccion_entrega`: se usa solo cuando el pedido es `delivery`.
- `detalle_pedido`: productos, cantidades y precios aplicados en el pedido.
- `pago`: resultado del pago simulado.
- `historial_estado_pedido`: historial de cambios de estado del pedido.
- `reabastecimiento`: ingreso de inventario por proveedor o carga administrativa.
- `detalle_reabastecimiento`: detalle por producto dentro de un reabastecimiento.
- `ajuste_inventario`: correccion directa de stock hecha por admin.

## 4. Relaciones y cardinalidades

| Relacion | Cardinalidad | Obligatoria | Regla de negocio |
| --- | --- | --- | --- |
| `ROL` -> `USUARIO` | 1:N | Todo usuario debe tener rol | Un rol puede pertenecer a muchos usuarios |
| `USUARIO` -> `SESION_USUARIO` | 1:N | Toda sesion pertenece a un usuario | Un usuario puede iniciar varias sesiones |
| `CATEGORIA` -> `PRODUCTO` | 1:N | Todo producto debe tener categoria | Una categoria agrupa muchos productos |
| `PROVEEDOR` -> `PRODUCTO` | 1:N opcional | El producto puede no tener proveedor inicial | Un proveedor puede abastecer varios productos |
| `USUARIO` -> `PEDIDO` | 1:N opcional | Un pedido puede no tener usuario por guest checkout | Un cliente registrado puede tener muchos pedidos |
| `PEDIDO` -> `DIRECCION_ENTREGA` | 1:0..1 | Solo aplica a `delivery` | Un pedido `pickup` no necesita direccion |
| `PEDIDO` -> `DETALLE_PEDIDO` | 1:N | Todo pedido debe tener al menos un detalle | Un detalle pertenece a un solo pedido |
| `PRODUCTO` -> `DETALLE_PEDIDO` | 1:N | Todo detalle referencia un producto | Un producto puede aparecer en muchos pedidos |
| `PEDIDO` -> `PAGO` | 1:1 | Todo pedido confirmado debe tener pago asociado | El modelo maneja un pago por pedido |
| `PEDIDO` -> `HISTORIAL_ESTADO_PEDIDO` | 1:N | El historial depende del pedido | Un pedido puede cambiar de estado varias veces |
| `USUARIO` -> `HISTORIAL_ESTADO_PEDIDO` | 1:N opcional | Puede ser `NULL` si el cambio fue automatico | Conserva trazabilidad del actor |
| `PROVEEDOR` -> `REABASTECIMIENTO` | 1:N opcional | Puede existir carga manual sin proveedor | Un proveedor puede atender muchos ingresos |
| `USUARIO` -> `REABASTECIMIENTO` | 1:N | Todo reabastecimiento debe tener admin responsable | |
| `REABASTECIMIENTO` -> `DETALLE_REABASTECIMIENTO` | 1:N | Todo ingreso debe tener detalle | |
| `PRODUCTO` -> `DETALLE_REABASTECIMIENTO` | 1:N | Todo detalle de reabastecimiento referencia producto | |
| `USUARIO` -> `AJUSTE_INVENTARIO` | 1:N | Todo ajuste directo debe quedar asociado a admin | |
| `PRODUCTO` -> `AJUSTE_INVENTARIO` | 1:N | Todo ajuste afecta un producto | |

## 5. DER documentado

```mermaid
erDiagram
    ROL ||--o{ USUARIO : define
    USUARIO ||--o{ SESION_USUARIO : abre
    CATEGORIA ||--o{ PRODUCTO : clasifica
    PROVEEDOR ||--o{ PRODUCTO : abastece
    USUARIO ||--o{ PEDIDO : realiza
    PEDIDO ||--o| DIRECCION_ENTREGA : usa
    PEDIDO ||--|{ DETALLE_PEDIDO : contiene
    PRODUCTO ||--o{ DETALLE_PEDIDO : participa
    PEDIDO ||--|| PAGO : registra
    PEDIDO ||--o{ HISTORIAL_ESTADO_PEDIDO : genera
    USUARIO ||--o{ HISTORIAL_ESTADO_PEDIDO : cambia
    PROVEEDOR ||--o{ REABASTECIMIENTO : atiende
    USUARIO ||--o{ REABASTECIMIENTO : registra
    REABASTECIMIENTO ||--|{ DETALLE_REABASTECIMIENTO : incluye
    PRODUCTO ||--o{ DETALLE_REABASTECIMIENTO : repone
    USUARIO ||--o{ AJUSTE_INVENTARIO : ejecuta
    PRODUCTO ||--o{ AJUSTE_INVENTARIO : ajusta

    ROL {
      smallint id_rol PK
      varchar nombre UK
    }

    USUARIO {
      bigint id_usuario PK
      smallint id_rol FK
      varchar email UK
      varchar password_hash
      varchar nombre
      varchar apellido
      varchar telefono
      boolean activo
      timestamp creado_en
    }

    SESION_USUARIO {
      uuid id_sesion PK
      bigint id_usuario FK
      varchar token_hash UK
      timestamp creada_en
      timestamp expira_en
      timestamp revocada_en
    }

    CATEGORIA {
      bigint id_categoria PK
      varchar nombre UK
      text descripcion
      boolean activa
    }

    PROVEEDOR {
      bigint id_proveedor PK
      varchar nombre
      varchar contacto
      varchar email
      varchar telefono
      boolean activo
    }

    PRODUCTO {
      bigint id_producto PK
      bigint id_categoria FK
      bigint id_proveedor FK
      varchar sku UK
      varchar nombre
      text descripcion
      numeric precio_unitario
      integer stock_actual
      boolean activo
      timestamp creado_en
      timestamp actualizado_en
    }

    PEDIDO {
      bigint id_pedido PK
      bigint id_usuario FK
      varchar codigo_publico UK
      varchar nombre_cliente
      varchar email_cliente
      varchar telefono_cliente
      varchar tipo_entrega
      varchar estado_pedido
      varchar estado_pago
      text nota_cliente
      timestamp creado_en
      timestamp confirmado_en
    }

    DIRECCION_ENTREGA {
      bigint id_direccion_entrega PK
      bigint id_pedido FK
      varchar linea_1
      varchar linea_2
      varchar ciudad
      varchar departamento
      varchar referencia
    }

    DETALLE_PEDIDO {
      bigint id_detalle_pedido PK
      bigint id_pedido FK
      bigint id_producto FK
      integer cantidad
      numeric precio_unitario
    }

    PAGO {
      bigint id_pago PK
      bigint id_pedido FK
      varchar metodo
      numeric monto
      varchar estado
      varchar codigo_simulado
      timestamp procesado_en
    }

    HISTORIAL_ESTADO_PEDIDO {
      bigint id_historial PK
      bigint id_pedido FK
      bigint id_usuario FK
      varchar estado_anterior
      varchar estado_nuevo
      text nota
      timestamp creado_en
    }

    REABASTECIMIENTO {
      bigint id_reabastecimiento PK
      bigint id_proveedor FK
      bigint id_admin FK
      text nota
      timestamp creado_en
    }

    DETALLE_REABASTECIMIENTO {
      bigint id_detalle_reab PK
      bigint id_reabastecimiento FK
      bigint id_producto FK
      integer cantidad
      numeric costo_unitario
    }

    AJUSTE_INVENTARIO {
      bigint id_ajuste PK
      bigint id_producto FK
      bigint id_admin FK
      integer cantidad_delta
      text motivo
      timestamp creado_en
    }
```

## 6. Modelo relacional documentado

Notacion relacional del esquema:

- `ROL(`id_rol` PK, nombre UQ)`
- `USUARIO(`id_usuario` PK, id_rol FK -> ROL.id_rol, email UQ, password_hash, nombre, apellido, telefono, activo, creado_en)`
- `SESION_USUARIO(`id_sesion` PK, id_usuario FK -> USUARIO.id_usuario, token_hash UQ, creada_en, expira_en, revocada_en)`
- `CATEGORIA(`id_categoria` PK, nombre UQ, descripcion, activa)`
- `PROVEEDOR(`id_proveedor` PK, nombre, contacto, email, telefono, activo)`
- `PRODUCTO(`id_producto` PK, id_categoria FK -> CATEGORIA.id_categoria, id_proveedor FK -> PROVEEDOR.id_proveedor NULL, sku UQ, nombre, descripcion, precio_unitario, stock_actual, activo, creado_en, actualizado_en)`
- `PEDIDO(`id_pedido` PK, id_usuario FK -> USUARIO.id_usuario NULL, codigo_publico UQ, nombre_cliente, email_cliente, telefono_cliente, tipo_entrega, estado_pedido, estado_pago, nota_cliente, creado_en, confirmado_en)`
- `DIRECCION_ENTREGA(`id_direccion_entrega` PK, id_pedido FK -> PEDIDO.id_pedido UQ, linea_1, linea_2, ciudad, departamento, referencia)`
- `DETALLE_PEDIDO(`id_detalle_pedido` PK, id_pedido FK -> PEDIDO.id_pedido, id_producto FK -> PRODUCTO.id_producto, cantidad, precio_unitario, UQ(id_pedido, id_producto))`
- `PAGO(`id_pago` PK, id_pedido FK -> PEDIDO.id_pedido UQ, metodo, monto, estado, codigo_simulado UQ, procesado_en)`
- `HISTORIAL_ESTADO_PEDIDO(`id_historial` PK, id_pedido FK -> PEDIDO.id_pedido, id_usuario FK -> USUARIO.id_usuario NULL, estado_anterior, estado_nuevo, nota, creado_en)`
- `REABASTECIMIENTO(`id_reabastecimiento` PK, id_proveedor FK -> PROVEEDOR.id_proveedor NULL, id_admin FK -> USUARIO.id_usuario, nota, creado_en)`
- `DETALLE_REABASTECIMIENTO(`id_detalle_reab` PK, id_reabastecimiento FK -> REABASTECIMIENTO.id_reabastecimiento, id_producto FK -> PRODUCTO.id_producto, cantidad, costo_unitario, UQ(id_reabastecimiento, id_producto))`
- `AJUSTE_INVENTARIO(`id_ajuste` PK, id_producto FK -> PRODUCTO.id_producto, id_admin FK -> USUARIO.id_usuario, cantidad_delta, motivo, creado_en)`

## 7. Normalizacion hasta 3FN

### 8.1 Punto de partida no normalizado

Si toda la operacion de tienda se intentara guardar en una sola estructura, aparecerian columnas repetidas y dependencias mezcladas, por ejemplo:

`VENTA_BRUTA(id_venta, fecha, cliente, email_cliente, telefono_cliente, direccion_delivery, tipo_entrega, producto_1, categoria_1, proveedor_1, cantidad_1, precio_1, producto_2, categoria_2, proveedor_2, cantidad_2, precio_2, pago_estado, pago_metodo, estado_actual, estado_previo, admin_que_modifico, restock_relacionado, ajuste_relacionado, ...)`

Ese diseno produciria:

- grupos repetitivos de productos por venta;
- repeticion de categoria y proveedor en cada linea;
- mezcla de datos opcionales de `delivery` con `pickup`;
- mezcla de resultado de pago con encabezado de pedido;
- perdida de trazabilidad de estados si solo existiera `estado_actual`;
- imposibilidad de justificar movimientos de stock por origen.

### 8.2 Dependencias funcionales principales

Las dependencias que justifican el modelo separado son:

- `ROL`
  - `id_rol -> nombre`
  - `nombre -> id_rol`
- `USUARIO`
  - `id_usuario -> id_rol, email, password_hash, nombre, apellido, telefono, activo, creado_en`
  - `email -> id_usuario, id_rol, password_hash, nombre, apellido, telefono, activo, creado_en`
- `SESION_USUARIO`
  - `id_sesion -> id_usuario, token_hash, creada_en, expira_en, revocada_en`
  - `token_hash -> id_sesion, id_usuario, creada_en, expira_en, revocada_en`
- `CATEGORIA`
  - `id_categoria -> nombre, descripcion, activa`
  - `nombre -> id_categoria, descripcion, activa`
- `PROVEEDOR`
  - `id_proveedor -> nombre, contacto, email, telefono, activo`
- `PRODUCTO`
  - `id_producto -> id_categoria, id_proveedor, sku, nombre, descripcion, precio_unitario, stock_actual, activo, creado_en, actualizado_en`
  - `sku -> id_producto, id_categoria, id_proveedor, nombre, descripcion, precio_unitario, stock_actual, activo, creado_en, actualizado_en`
- `PEDIDO`
  - `id_pedido -> id_usuario, codigo_publico, nombre_cliente, email_cliente, telefono_cliente, tipo_entrega, estado_pedido, estado_pago, nota_cliente, creado_en, confirmado_en`
  - `codigo_publico -> id_pedido, id_usuario, nombre_cliente, email_cliente, telefono_cliente, tipo_entrega, estado_pedido, estado_pago, nota_cliente, creado_en, confirmado_en`
- `DIRECCION_ENTREGA`
  - `id_direccion_entrega -> id_pedido, linea_1, linea_2, ciudad, departamento, referencia`
  - `id_pedido -> linea_1, linea_2, ciudad, departamento, referencia`
- `DETALLE_PEDIDO`
  - clave natural de negocio: `(id_pedido, id_producto) -> cantidad, precio_unitario`
  - la PK sustituta `id_detalle_pedido` identifica la fila, pero la dependencia de negocio sigue siendo la compuesta
- `PAGO`
  - `id_pago -> id_pedido, metodo, monto, estado, codigo_simulado, procesado_en`
  - `id_pedido -> metodo, monto, estado, codigo_simulado, procesado_en`
  - `codigo_simulado -> id_pago, id_pedido, metodo, monto, estado, procesado_en`
- `HISTORIAL_ESTADO_PEDIDO`
  - `id_historial -> id_pedido, id_usuario, estado_anterior, estado_nuevo, nota, creado_en`
- `REABASTECIMIENTO`
  - `id_reabastecimiento -> id_proveedor, id_admin, nota, creado_en`
- `DETALLE_REABASTECIMIENTO`
  - clave natural de negocio: `(id_reabastecimiento, id_producto) -> cantidad, costo_unitario`
- `AJUSTE_INVENTARIO`
  - `id_ajuste -> id_producto, id_admin, cantidad_delta, motivo, creado_en`

### 8.3 Primera forma normal (1FN)

El modelo cumple 1FN porque:

- cada tabla tiene clave primaria;
- todos los atributos son atomicos;
- los grupos repetitivos se separan en tablas detalle:
  - `DETALLE_PEDIDO`
  - `DETALLE_REABASTECIMIENTO`
- la direccion se saca de `PEDIDO` hacia `DIRECCION_ENTREGA`, evitando columnas opcionales repetidas o nulas para `pickup`.

### 8.4 Segunda forma normal (2FN)

El modelo cumple 2FN porque los atributos no clave dependen de la clave completa de cada relacion:

- en `DETALLE_PEDIDO`, `cantidad` y `precio_unitario` dependen de la combinacion `(id_pedido, id_producto)`, no solo del pedido ni solo del producto;
- en `DETALLE_REABASTECIMIENTO`, `cantidad` y `costo_unitario` dependen del detalle completo del evento;
- las tablas maestras (`ROL`, `CATEGORIA`, `PROVEEDOR`) no cargan atributos que dependan parcialmente de una clave compuesta, porque no usan ese tipo de clave.

Aunque el esquema fisico usa PK sustitutas en las tablas detalle, la dependencia de negocio sigue siendo la compuesta, y por eso se conserva una restriccion `UNIQUE` sobre esas combinaciones.

### 8.5 Tercera forma normal (3FN)

El modelo cumple 3FN por estas separaciones:

- `ROL` se separa de `USUARIO`, evitando que el nombre del rol dependa transitivamente del usuario.
- `CATEGORIA` y `PROVEEDOR` se separan de `PRODUCTO`, evitando repetir datos de clasificacion y abastecimiento.
- `DIRECCION_ENTREGA` se separa de `PEDIDO`, porque esos atributos solo aplican cuando `tipo_entrega = 'delivery'`.
- `PAGO` se separa de `PEDIDO`, porque el resultado del cobro no debe depender transitivamente de datos del cliente o del pedido.
- `HISTORIAL_ESTADO_PEDIDO` se separa de `PEDIDO`, para conservar todos los cambios de estado en lugar de sobrescribir informacion.
- `REABASTECIMIENTO`, `DETALLE_REABASTECIMIENTO` y `AJUSTE_INVENTARIO` separan los origenes del cambio de stock.

### 8.6 Decisiones pragmaticas que se documentan explicitamente

Hay dos decisiones que no rompen 3FN y conviene dejar justificadas:

- `PRODUCTO.stock_actual` se almacena fisicamente en lugar de calcularse siempre desde movimientos. Es una decision operativa para simplificar consultas de catalogo, admin y validacion de checkout. La trazabilidad sigue existiendo en `DETALLE_PEDIDO`, `DETALLE_REABASTECIMIENTO` y `AJUSTE_INVENTARIO`.
- `PEDIDO.nombre_cliente`, `PEDIDO.email_cliente` y `PEDIDO.telefono_cliente` guardan la fotografia del momento de compra. Aunque el pedido pueda estar ligado a `USUARIO`, estos datos no dependen transitivamente del usuario sino del evento comercial concreto.

## 8. DDL completo documentado

El DDL ejecutable del proyecto esta en `db/init/001_schema.sql`. La tabla siguiente resume las restricciones importantes para cada relacion.

| Tabla | PK | FK | Columnas `NOT NULL` y restricciones clave |
| --- | --- | --- | --- |
| `rol` | `id_rol` | - | `nombre` `UNIQUE` |
| `usuario` | `id_usuario` | `id_rol -> rol.id_rol` | `id_rol`, `email`, `password_hash`, `nombre`, `apellido`, `activo`, `creado_en`; `email` `UNIQUE` |
| `sesion_usuario` | `id_sesion` | `id_usuario -> usuario.id_usuario` | `id_usuario`, `token_hash`, `creada_en`, `expira_en`; `token_hash` `UNIQUE` |
| `categoria` | `id_categoria` | - | `nombre`, `activa`; `nombre` `UNIQUE` |
| `proveedor` | `id_proveedor` | - | `nombre`, `activo` |
| `producto` | `id_producto` | `id_categoria -> categoria.id_categoria`, `id_proveedor -> proveedor.id_proveedor` | `id_categoria`, `sku`, `nombre`, `precio_unitario`, `stock_actual`, `activo`, `creado_en`, `actualizado_en`; `sku` `UNIQUE`; `CHECK(precio_unitario >= 0)`; `CHECK(stock_actual >= 0)` |
| `pedido` | `id_pedido` | `id_usuario -> usuario.id_usuario` | `codigo_publico`, `nombre_cliente`, `email_cliente`, `tipo_entrega`, `estado_pedido`, `estado_pago`, `creado_en`; `codigo_publico` `UNIQUE`; `CHECK(tipo_entrega IN ('delivery', 'pickup'))` |
| `direccion_entrega` | `id_direccion_entrega` | `id_pedido -> pedido.id_pedido` | `id_pedido`, `linea_1`, `ciudad`, `departamento`; `id_pedido` `UNIQUE` para respetar la relacion 1:1 |
| `detalle_pedido` | `id_detalle_pedido` | `id_pedido -> pedido.id_pedido`, `id_producto -> producto.id_producto` | `id_pedido`, `id_producto`, `cantidad`, `precio_unitario`; `CHECK(cantidad > 0)`; `CHECK(precio_unitario >= 0)`; `UNIQUE(id_pedido, id_producto)` |
| `pago` | `id_pago` | `id_pedido -> pedido.id_pedido` | `id_pedido`, `metodo`, `monto`, `estado`, `codigo_simulado`; `id_pedido` `UNIQUE`; `codigo_simulado` `UNIQUE`; `CHECK(metodo IN ('efectivo', 'tarjeta', 'transferencia'))`; `CHECK(estado IN ('pendiente', 'aprobado', 'rechazado'))` |
| `historial_estado_pedido` | `id_historial` | `id_pedido -> pedido.id_pedido`, `id_usuario -> usuario.id_usuario` | `id_pedido`, `estado_nuevo`, `creado_en` |
| `reabastecimiento` | `id_reabastecimiento` | `id_proveedor -> proveedor.id_proveedor`, `id_admin -> usuario.id_usuario` | `id_admin`, `creado_en` |
| `detalle_reabastecimiento` | `id_detalle_reab` | `id_reabastecimiento -> reabastecimiento.id_reabastecimiento`, `id_producto -> producto.id_producto` | `id_reabastecimiento`, `id_producto`, `cantidad`, `costo_unitario`; `CHECK(cantidad > 0)`; `CHECK(costo_unitario >= 0)`; `UNIQUE(id_reabastecimiento, id_producto)` |
| `ajuste_inventario` | `id_ajuste` | `id_producto -> producto.id_producto`, `id_admin -> usuario.id_usuario` | `id_producto`, `id_admin`, `cantidad_delta`, `motivo`, `creado_en` |

Notas de implementacion fisica:

- El archivo SQL ya incluye `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE` y `CHECK`.
- El archivo tambien define la `VIEW` `vw_resumen_ventas`, util para la parte SQL/reportes del proyecto.
- La creacion de tablas respeta el orden de dependencias foraneas para que PostgreSQL pueda inicializar la base desde Docker.

## 9. Indices y objetos auxiliares

### 9.1 Indices explicitamente definidos

El esquema actual define estos indices:

- `CREATE INDEX idx_producto_categoria ON producto(id_categoria);`
  - Justificacion: acelera filtros de catalogo y CRUD admin por categoria.
- `CREATE INDEX idx_producto_stock_actual ON producto(stock_actual);`
  - Justificacion: acelera listados de bajo stock y revisiones de inventario.
- `CREATE INDEX idx_pedido_creado_en ON pedido(creado_en);`
  - Justificacion: acelera reportes por fecha y ordenamientos cronologicos.
- `CREATE INDEX idx_pedido_usuario_creado ON pedido(id_usuario, creado_en);`
  - Justificacion: acelera historial de pedidos por cliente.
- `CREATE INDEX idx_detalle_pedido_producto ON detalle_pedido(id_producto);`
  - Justificacion: acelera reportes por producto y joins con ventas.
- `CREATE INDEX idx_pago_estado ON pago(estado);`
  - Justificacion: acelera filtros de pagos aprobados, rechazados o pendientes.

### 9.2 VIEW incluida en el esquema

La base ya define:

- `vw_resumen_ventas`

Su objetivo es exponer por pedido:

- identificador interno;
- codigo publico;
- fecha;
- tipo de entrega;
- estado del pedido;
- estado del pago;
- total monetario calculado desde `detalle_pedido`.

Esto mantiene la logica agregada dentro de SQL y deja una pieza reutilizable para el backend.

## 10. Datos de prueba documentados

El archivo `db/init/002_seed.sql` contiene datos iniciales para levantar y probar el sistema. Actualmente carga roles, usuarios de prueba, categorias, proveedores y productos. Las tablas transaccionales quedan listas para registrar pedidos, direcciones, detalles, pagos, cambios de estado, reabastecimientos, ajustes de inventario y sesiones de usuario.

## 11. Flujos transaccionales que este diseno soporta

### 11.1 Checkout

El checkout crea el pedido, registra el pago y descuenta stock dentro de una transaccion consistente. La operacion inicia con `BEGIN` y `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`, valida el carrito, bloquea los productos con `SELECT ... FOR UPDATE`, verifica stock, inserta `pedido`, `detalle_pedido` y `pago`, y despues confirma o rechaza la compra segun el resultado del pago simulado. Si el pago se aprueba, se descuenta `producto.stock_actual` y se registra el cambio en `historial_estado_pedido`; si se rechaza, el stock no cambia. Cualquier error, conflicto o falta de stock termina en `ROLLBACK`.

### 11.2 Catalogo e inventario

Las altas y actualizaciones de categorias/productos pasan por procedimientos almacenados para cumplir el requisito de Proyecto 3. El backend tambien usa SQLAlchemy ORM para operaciones CRUD concretas como sesiones, usuarios cliente y eliminaciones controladas de categorias/productos.

### 11.3 Ventas

El cambio de estado de una venta se hace con una transaccion explicita desde backend e invoca `sp_update_sale_status`. Asi el cambio de `pedido.estado_pedido` y la fila de `historial_estado_pedido` quedan juntos.

### 11.4 Reabastecimiento

El reabastecimiento aumenta inventario con trazabilidad. La transaccion crea el encabezado con `sp_create_restock`, agrega lineas con `sp_add_restock_detail` y actualiza el stock de los productos afectados. Si ocurre un error, la operacion se revierte con `ROLLBACK`.

### 11.5 Ajuste directo de inventario

El ajuste directo usa `sp_apply_inventory_adjustment`. La operacion bloquea el producto, registra la fila en `ajuste_inventario`, actualiza `stock_actual` y valida que el inventario no quede negativo antes de confirmar.

### 11.6 Login con sesion

El login valida credenciales contra `usuario`, genera un token o identificador de sesion y guarda su hash en `sesion_usuario`. El logout conserva trazabilidad marcando `revocada_en`.

## 12. Uso de ORM y SQL explicito

Proyecto 3 usa SQLAlchemy ORM de forma obligatoria en operaciones CRUD reales del backend: usuarios cliente, sesiones de usuario y eliminaciones controladas de categorias/productos. El objetivo es cubrir el requisito de ORM sin perder la parte SQL que corresponde a la materia.

El SQL explicito se mantiene donde aporta mas claridad para bases de datos: reportes, agregaciones, uso de `vw_resumen_ventas`, bloqueo de filas, llamadas a procedimientos almacenados y transacciones manuales. Por eso el proyecto no queda como "solo ORM"; usa ORM para CRUD y SQL directo para las partes avanzadas.

## 13. Procedimientos almacenados

Los procedimientos esperados para esta entrega son:

| Procedimiento | Uso desde backend |
| --- | --- |
| `sp_create_category` | Crear categoria desde el panel de catalogo |
| `sp_update_category` | Actualizar categoria existente |
| `sp_create_product` | Crear producto con SKU, precio, categoria y stock |
| `sp_update_product` | Actualizar datos de producto |
| `sp_update_sale_status` | Cambiar estado de venta y dejar historial |
| `sp_apply_inventory_adjustment` | Registrar ajuste directo y modificar stock |
| `sp_create_restock` | Crear encabezado de reabastecimiento |
| `sp_add_restock_detail` | Agregar detalle de reabastecimiento y sumar inventario |

Estos procedimientos se invocan desde FastAPI. Los permisos de ejecucion deben seguir los mismos roles DBMS del modulo correspondiente: catalogo para `app_admin` y `app_inventory`, ventas para `app_admin` y `app_sales`, inventario para `app_admin` y `app_inventory`.

## 14. Modelo de seguridad DBMS

El control de acceso DBMS se define en `db/init/003_security_roles.sql`. Para Proyecto 3 se usan exactamente cinco roles operativos de PostgreSQL, creados con `CREATE ROLE` y ajustados con `GRANT` y `REVOKE`.

### 14.1 Mapeo explicito: rol de aplicacion a rol DBMS

| Rol de aplicacion (`rol.nombre`) | Rol DBMS operativo | Uso principal |
| --- | --- | --- |
| `admin` | `app_admin` | Gestion completa de catalogo, inventario, pedidos, reportes y auditoria operativa |
| `inventario` | `app_inventory` | Catalogo, stock, ajustes y reabastecimientos |
| `ventas` | `app_sales` | Pedidos, pagos y cambios de estado de venta |
| `reportes` | `app_reporting` | Lectura para reportes, vistas y exportaciones |
| `cliente` | `app_customer` | Registro, sesion, catalogo, checkout autenticado y pedidos propios |

No se documenta un sexto rol DBMS para invitados. El checkout publico sigue existiendo como flujo de la aplicacion, pero el acceso a la base se controla desde backend.

### 14.2 Matriz de permisos por rol DBMS

| Nombre del rol DBMS | Tablas accesibles | Operaciones permitidas | Restricciones |
| --- | --- | --- | --- |
| `app_admin` | Todas las tablas del esquema `public` y `vw_resumen_ventas` | `SELECT/INSERT/UPDATE/DELETE` | Acceso operativo completo |
| `app_inventory` | `categoria`, `proveedor`, `producto`, `reabastecimiento`, `detalle_reabastecimiento`, `ajuste_inventario`, pedidos para consulta | Lectura de catalogo y pedidos; escritura en catalogo e inventario | Sin permisos sobre `usuario`, `sesion_usuario` ni `pago` |
| `app_sales` | `producto`, `categoria`, `proveedor`, `pedido`, `direccion_entrega`, `detalle_pedido`, `pago`, `historial_estado_pedido` | Lectura de catalogo; creacion y actualizacion del ciclo de venta | Sin administracion de usuarios ni inventario |
| `app_reporting` | Tablas del esquema `public` y `vw_resumen_ventas` | `SELECT` | Sin `INSERT`, `UPDATE` ni `DELETE` |
| `app_customer` | `usuario`, `sesion_usuario`, `categoria`, `producto`, `pedido`, `direccion_entrega`, `detalle_pedido`, `pago`, `historial_estado_pedido`, `vw_resumen_ventas` | Registro/sesion, lectura de catalogo y creacion de pedidos propios | Sin acceso administrativo a roles, proveedores, reabastecimientos ni ajustes |

### 14.3 Ejemplos de `GRANT` y `REVOKE`

Ejemplos representativos del script:

- `REVOKE ALL ON SCHEMA public FROM PUBLIC;`
- `GRANT USAGE ON SCHEMA public TO app_admin, app_inventory, app_sales, app_reporting, app_customer;`
- `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_admin;`
- `GRANT SELECT, INSERT ON reabastecimiento, detalle_reabastecimiento, ajuste_inventario TO app_inventory;`
- `GRANT SELECT, INSERT, UPDATE ON pedido, direccion_entrega, detalle_pedido, pago, historial_estado_pedido TO app_sales;`
- `GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reporting;`
- `GRANT SELECT, INSERT, UPDATE ON usuario TO app_customer;`
- `REVOKE ALL ON rol, proveedor, reabastecimiento, detalle_reabastecimiento, ajuste_inventario FROM app_customer;`

### 14.4 Permisos sobre vistas y procedimientos

`vw_resumen_ventas` se mantiene para reportes. `app_reporting` tiene lectura, `app_admin` entra por su permiso general y los demas roles solo deben recibir acceso si una pantalla lo necesita.

Los procedimientos almacenados deben tener `GRANT EXECUTE` solo para los roles que los usan. Por ejemplo, los procedimientos de catalogo para `app_admin` y `app_inventory`, el cambio de estado para `app_admin` y `app_sales`, y los procedimientos de inventario para `app_admin` y `app_inventory`.

## 15. Resumen

El diseno separa la explicacion academica en este documento, la traduccion fisica en `db/init/001_schema.sql`, los datos iniciales en `db/init/002_seed.sql`, la seguridad DBMS en `db/init/003_security_roles.sql` y las operaciones avanzadas en procedimientos almacenados llamados desde FastAPI.
