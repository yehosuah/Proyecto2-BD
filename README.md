# Proyecto 3 - Bases de Datos

Aplicacion full stack para el Proyecto 3. Se mantiene la tienda del Proyecto 2, pero ahora la entrega se trabaja en la misma repo usando la rama `proyecto-3`.

El stack usado es:

- FastAPI para el backend.
- Vue 3 + Vite para el frontend.
- PostgreSQL como DBMS.
- Docker Compose para levantar todo desde cero.

La aplicacion conserva el storefront publico, cuentas de cliente, checkout, panel de administracion, ventas, inventario y reportes. Para Proyecto 3 se agrega el enfoque de seguridad por roles DBMS, procedimientos almacenados invocados desde backend, ORM obligatorio y transacciones explicitas.

## Rama de entrega

La entrega debe revisarse en esta rama:

```bash
git checkout proyecto-3
```

Si se clona desde cero:

```bash
git clone <url-del-repo>
cd Proyecto2-BD
git checkout proyecto-3
```

## Levantar desde cero

Requisitos: Docker Desktop o Docker Engine con el plugin de Compose, Git y los puertos `5173`, `8000` y `55432` libres.

Desde la raiz del proyecto:

```bash
cp .env.example .env
docker compose up --build
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Servicios esperados:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- PostgreSQL: `localhost:55432`

La base se crea desde los scripts de `db/init/` cuando el volumen esta vacio. Si ya existia una base local y se quiere iniciar de cero:

```bash
docker compose down -v
docker compose up --build
```

## Credenciales de base de datos

El Proyecto 3 usa estas credenciales en `.env`:

```env
POSTGRES_DB=proyecto3_bd
POSTGRES_USER=proy3
POSTGRES_PASSWORD=secret
POSTGRES_PORT=55432
```

El backend se conecta con `DATABASE_URL` dentro de Docker usando el servicio `db`.

## Usuarios de prueba

Hay un usuario de prueba por rol de aplicacion:

| Rol | Usuario | Password |
| --- | --- | --- |
| `admin` | `admin@proyecto3.local` | `admin123` |
| `inventario` | `inventario@proyecto3.local` | `inventario123` |
| `ventas` | `ventas@proyecto3.local` | `ventas123` |
| `reportes` | `reportes@proyecto3.local` | `reportes123` |
| `cliente` | `cliente@proyecto3.local` | `cliente123` |

## Superficies principales

La tienda publica sigue disponible sin login:

- `/`
- `/catalog`
- `/catalog/:sku`
- `/checkout`
- `/checkout/resultado/:codigo`

La cuenta requiere sesion:

- `/account/profile`
- `/account/orders`
- `/account/orders/:codigo`

El panel interno se protege por rol:

- `admin`: acceso completo a dashboard, catalogo, inventario, ventas y reportes.
- `inventario`: productos, categorias, ajustes y reabastecimientos.
- `ventas`: listado de ventas, detalle de venta y cambio de estado.
- `reportes`: dashboard de reportes y exportacion.
- `cliente`: perfil, pedidos propios y compra autenticada.

Las rutas del frontend validan el rol antes de mostrar vistas internas, y el backend vuelve a validar el mismo permiso antes de ejecutar la operacion.

## Roles DBMS

El script de seguridad define exactamente cinco roles de PostgreSQL con `CREATE ROLE`:

- `app_admin`
- `app_inventory`
- `app_sales`
- `app_reporting`
- `app_customer`

`db/init/003_security_roles.sql` cierra privilegios por defecto con `REVOKE` y despues entrega permisos puntuales con `GRANT`. No se usa rol DBMS de invitado; el flujo publico pasa por los permisos controlados del backend y por el rol correspondiente al caso de uso.

## ORM y SQL

El backend usa SQLAlchemy ORM en operaciones CRUD de usuarios, sesiones y eliminaciones controladas de categorias/productos. Para reportes avanzados, agregaciones, vistas, transacciones fuertes y llamadas a procedimientos almacenados, se mantiene SQL explicito desde el backend.

Esta combinacion cumple el requisito de ORM obligatorio sin esconder la parte SQL que importa para la entrega de bases de datos.

## Procedimientos almacenados

El backend invoca procedimientos almacenados para operaciones que deben quedar encapsuladas en PostgreSQL:

- `sp_create_category`
- `sp_update_category`
- `sp_create_product`
- `sp_update_product`
- `sp_update_sale_status`
- `sp_apply_inventory_adjustment`
- `sp_create_restock`
- `sp_add_restock_detail`

Estos procedimientos cubren catalogo, productos, cambios de estado de venta, ajustes de inventario y reabastecimientos.

## Transacciones

Las operaciones criticas se manejan con transacciones explicitas. El checkout valida stock, crea pedido, detalle, pago e historial dentro de una misma unidad de trabajo. Inventario y reabastecimiento tambien deben confirmar todo junto o revertir todo con `ROLLBACK`.

## Verificacion rapida

Con los servicios levantados:

```bash
docker compose ps
docker compose exec -T backend pytest -q
```

Tambien se puede probar manualmente:

- login con cada usuario de prueba;
- CRUD de categorias y productos;
- checkout aprobado y rechazado;
- cambio de estado de una venta;
- ajuste de inventario;
- reabastecimiento;
- reportes y exportacion CSV.

## Apagar el proyecto

Para apagar sin borrar datos:

```bash
docker compose down
```

Para borrar contenedores y datos locales de PostgreSQL:

```bash
docker compose down -v
```
