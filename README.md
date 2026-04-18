# Proyecto2-BD

Aplicacion full stack para `Proyecto 2` de `cc3088 - Bases de Datos 1`. El sistema cubre:

- storefront publico con catalogo y checkout
- cuentas cliente con perfil e historial de pedidos
- panel administrativo con CRUD, ventas y reportes
- PostgreSQL con SQL explicito y transacciones marcadas manualmente

## Estructura

- `frontend/`: Vue 3 + Vite
- `backend/`: FastAPI + `psycopg`
- `db/init/001_schema.sql`: esquema, indices y `vw_resumen_ventas`
- `db/init/002_seed.sql`: burner data coherente para demo y grading
- `diseno-bd.md`: DER, modelo relacional y normalizacion

## Credenciales requeridas

Base de datos:

- usuario: `proy2`
- password: `secret`

Credenciales demo de la aplicacion:

- admin: `admin@proyecto2.local` / `admin123`
- cliente: `cliente@proyecto2.local` / `client123`

## Levantar desde cero

```bash
cp .env.example .env
docker compose up --build
```

Servicios esperados:

- frontend: [http://localhost:5173](http://localhost:5173)
- backend: [http://localhost:8000](http://localhost:8000)
- postgres: `localhost:55432`

Prueba rapida recomendada del backend:

```bash
docker compose exec -T backend pytest tests/test_app_structure.py -q
```

## Superficies principales

Storefront:

- `/`
- `/catalog`
- `/catalog/:sku`
- `/checkout`
- `/checkout/resultado/:codigo`

Cuenta:

- `/account/login`
- `/account/register`
- `/account/profile`
- `/account/orders`

Admin:

- `/admin`
- `/admin/products`
- `/admin/categories`
- `/admin/sales`
- `/admin/reports`

## Reglas importantes del proyecto

- No se usa ORM.
- Las consultas SQL relevantes se ejecutan desde la aplicacion web.
- El checkout usa transaccion explicita con `SERIALIZABLE`.
- El reporte principal visible/exportable es `ventas por rango de fechas`.
- La exportacion avanzada incluida en esta entrega es `CSV`.

## Datos de prueba

`db/init/002_seed.sql` genera:

- 25+ filas por tablas de negocio/transaccionales evaluables
- productos con stock bajo
- pedidos guest y pedidos de usuarios registrados
- pagos aprobados y rechazados
- historial de estados
- restocks y ajustes de inventario

Esto permite probar:

- joins y subqueries visibles en UI
- agregaciones y `HAVING`
- una consulta con `CTE`
- una `VIEW` usada por el backend
- CRUD administrativo
- historial de pedidos
- exportacion CSV
