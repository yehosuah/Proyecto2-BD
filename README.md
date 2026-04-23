# Proyecto2-BD

Base scaffold for `Proyecto 2` of `cc3088 - Bases de Datos 1`. The repository now contains the approved architecture foundation:

- `frontend/`: Vue 3 + Vite single app for storefront, account, and admin surfaces
- `backend/`: FastAPI app with explicit domain partitions and no ORM
- `db/init/`: PostgreSQL schema, seed data, and view bootstrap
- `diseno-bd.md`: current database design draft and transaction notes

## Current architecture

- `storefront` routes for public catalog and checkout
- `account` routes for login, profile, and order history
- `admin` routes for dashboard, products, categories, sales, and reports
- `backend` domain partitions:
  - `auth`
  - `catalog`
  - `orders`
  - `inventory`
  - `reporting`
  - `admin`

## Environment

Copy the example file before running containers:

```bash
cp .env.example .env
```

Required grading credentials are already set in `.env.example`:

- DB user: `proy2`
- DB password: `secret`

## Run the foundation

```bash
docker compose up --build
```

Expected services:

- PostgreSQL on `localhost:5432`
- FastAPI on `http://localhost:8000`
- Vue app on `http://localhost:5173`

## Seeded demo users

The SQL seed currently inserts:

- admin demo: `admin@proyecto2.local`
- client demo: `cliente@proyecto2.local`

These rows are present now for grading-oriented flows. Real login behavior is not implemented yet in this scaffold phase.

## Next implementation targets

- real SQL repositories and transactions in FastAPI
- admin CRUD for products and categories
- storefront catalog, cart, and checkout flow
- account auth and order history
- reporting queries surfaced in the UI
