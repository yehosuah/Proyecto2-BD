# Proyecto2-BD

Proyecto 2 del curso `cc3088 - Bases de Datos 1`. La aplicacion modela una tienda con control de inventario, ventas, reportes y una base de datos relacional en PostgreSQL.

- `frontend/`: interfaz web en Vue 3 + Vite
- `backend/`: API en FastAPI con SQL explicito
- `db/init/`: scripts de inicializacion de PostgreSQL
- `diseno-bd.md`: diseno de base de datos, modelo relacional y normalizacion

## Diseno de base de datos

La documentacion principal esta dividida asi:

- `diseno-bd.md`: entidades, relaciones, DER, modelo relacional, normalizacion a 3FN e indices
- `db/init/001_schema.sql`: DDL ejecutable con tablas, llaves, restricciones, indices y `vw_resumen_ventas`
- `db/init/002_seed.sql`: datos iniciales para probar el arranque del sistema

## Arquitectura

- rutas publicas para inicio, catalogo y checkout
- rutas de cuenta para login, perfil e historial de pedidos
- rutas administrativas para productos, categorias, ventas y reportes
- modulos del backend:
  - `auth`
  - `catalog`
  - `orders`
  - `inventory`
  - `reporting`
  - `admin`

## Variables de entorno

Antes de levantar Docker, copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Credenciales de base de datos usadas por el proyecto:

- usuario: `proy2`
- password: `secret`

## Ejecucion

```bash
docker compose up --build
```

Servicios esperados:

- PostgreSQL on `localhost:5432`
- FastAPI on `http://localhost:8000`
- Vue app on `http://localhost:5173`

## Usuarios iniciales

El script de datos iniciales crea dos usuarios para probar los flujos principales:

- administrador: `admin@proyecto2.local`
- cliente: `cliente@proyecto2.local`
