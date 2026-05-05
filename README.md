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

## Requisitos para levantar el container

Funciona igual en Windows, macOS y Linux mientras la maquina tenga:

- Docker Desktop en Windows o macOS, con Docker Compose incluido.
- Docker Engine + Docker Compose plugin en Linux.
- Git o una forma de descargar el repositorio completo.
- Puertos libres `5173`, `8000` y `55432`.

En Windows se recomienda correr los comandos desde PowerShell, Git Bash o WSL. Si se usa Docker Desktop, debe estar abierto antes de ejecutar `docker compose`.

## Levantar desde cero en cualquier OS

Primero entrar a la carpeta raiz del proyecto, donde esta `docker-compose.yml`.

macOS, Linux, Git Bash o WSL:

```bash
cp .env.example .env
docker compose up --build
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Windows CMD:

```bat
copy .env.example .env
docker compose up --build
```

El primer arranque puede tardar porque descarga PostgreSQL, Python y Node, instala dependencias, construye el frontend y crea la base con los scripts de `db/init/`.

Servicios esperados:

- frontend: [http://localhost:5173](http://localhost:5173)
- backend: [http://localhost:8000](http://localhost:8000)
- postgres: `localhost:55432`

La base se inicializa con:

- base: `proyecto2_bd`
- usuario: `proy2`
- password: `secret`
- puerto local: `55432`

El backend espera a que PostgreSQL este saludable antes de iniciar. Si el frontend abre antes que el backend termine de cargar, esperar unos segundos y refrescar la pagina.

Prueba rapida recomendada del backend:

```bash
docker compose exec -T backend pytest tests/test_app_structure.py -q
```

Tambien se puede revisar el estado de los servicios con:

```bash
docker compose ps
```

## Cambiar puertos si ya estan ocupados

Editar `.env` antes de levantar el proyecto. Por ejemplo:

```env
BACKEND_PORT=8001
FRONTEND_PORT=5174
POSTGRES_PORT=55433
```

Luego levantar otra vez:

```bash
docker compose up --build
```

Si se cambia `BACKEND_PORT`, el frontend queda configurado para llamar a ese puerto durante el build. Por eso conviene reconstruir con `--build`.

## Apagar, reiniciar y limpiar

Apagar sin borrar datos:

```bash
docker compose down
```

Volver a levantar usando los datos ya creados:

```bash
docker compose up
```

Reconstruir imagenes despues de cambios de dependencias o puertos:

```bash
docker compose up --build
```

Borrar contenedores y tambien reiniciar la base de datos desde cero:

```bash
docker compose down -v
docker compose up --build
```

Usar `down -v` solo cuando se quiera perder la data local de PostgreSQL y volver a cargar los scripts iniciales.

## Problemas comunes

Si sale que un puerto ya esta en uso, cambiar `BACKEND_PORT`, `FRONTEND_PORT` o `POSTGRES_PORT` en `.env` y levantar con `docker compose up --build`.

Si Docker no reconoce `docker compose`, actualizar Docker Desktop o instalar el Compose plugin. En instalaciones viejas podria existir `docker-compose`, pero este proyecto esta documentado para el comando actual `docker compose`.

Si el backend no conecta a la base, revisar:

```bash
docker compose ps
docker compose logs db
docker compose logs backend
```

Si se necesita recrear la base porque los scripts iniciales cambiaron, usar:

```bash
docker compose down -v
docker compose up --build
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
