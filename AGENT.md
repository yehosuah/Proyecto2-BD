# AGENT.md

## 1. Project Summary

This repository contains the foundation scaffold for `Proyecto 2` of `cc3088 - Bases de Datos 1 (Ciclo 1, 2026)`. The approved architecture is a single Vue frontend, a single FastAPI backend with domain-partitioned modules, and one PostgreSQL database initialized through Docker Compose. The source of truth for assignment requirements remains `/Users/yehosuahercules/Downloads/Proyecto_2.pdf`.

## 2. Repository Map

- `frontend/`: Vue 3 + Vite application for storefront, account, and admin surfaces.
- `backend/`: FastAPI application, tests, Dockerfile, and Python dependency files.
- `db/init/`: PostgreSQL schema and seed scripts loaded by the database container.
- `docs/superpowers/plans/`: implementation plan artifacts for scaffold work.
- `diseno-bd.md`: approved draft for the current relational model, normalization, and transaction flows.
- `README.md`: local setup and repo overview.
- `AGENT.md`: repo guide for future implementation work.
- `.git/`: git metadata only; do not edit directly.

Current repo state: architecture and starter runtime files exist, but feature logic is still mostly placeholder.

## 3. Commands

Root workflow:

- `cp .env.example .env`
- `docker compose up --build`
- `docker compose config`

Backend checks:

- `python3 -m compileall backend/app`
- `python3 -m pytest backend/tests/test_app_structure.py -q`

Frontend checks:

- `node --check frontend/src/main.js`
- `node --check frontend/src/router/index.js`

Note: host-level `pytest` is not currently installed in this environment; use a local `.venv` or the backend container when you need to run Python tests locally.

## 4. Conventions

Assignment constraints extracted from the PDF:

- Build a web application for a store domain with products, categories, suppliers, customers, employees, purchases, sale details, stock control, and sales reporting.
- Use a relational DBMS: MySQL, PostgreSQL, SQLite, or SQL Server.
- Use explicit SQL queries. Do not adopt an ORM that hides SQL generation.
- Define all infrastructure in `docker-compose.yml`: database, backend, and frontend. This scaffold already follows that shape.
- Manage credentials through `.env`; commit `.env.example`.
- Database grading credentials are fixed: user `proy2`, password `secret`.
- Mark transactions explicitly in code with `BEGIN` / `COMMIT` / `ROLLBACK` or equivalent.
- The README must explain how to boot the project from zero.

Required rubric coverage to keep in mind before implementing:

- Database design artifacts: ER diagram, relational model, 3NF justification, DDL, seed data, explicit indexes.
- UI-backed SQL features: joins, subqueries, grouped reports, at least one CTE, at least one backend-used view, and at least one explicit transaction with rollback handling.
- Web features: CRUD for at least 2 entities, at least 1 visible report, and visible user-facing error handling.
- Optional advanced points: authentication and CSV/PDF export.

Project-specific decisions already approved:

- Guest-first storefront checkout is allowed.
- Registered clients also have profile and order history.
- Admin is seeded in the database and can access both admin and client-facing surfaces.
- Sales originate only from the storefront; admin sales UI is read/manage only.
- Products are single-SKU items.
- Payment is simulated and fully internal.
- Fulfillment supports both `delivery` and `pickup`.
- Inventory uses both lightweight restock entries and direct stock adjustments.
- Checkout-critical SQL paths should be designed around explicit serializable transactions.

## 5. Validation Before Handoff

Once implementation starts, future agents should not claim progress complete unless they verify:

- The repo still boots from `docker compose up`.
- The configured DB credentials remain `proy2` / `secret`.
- SQL-heavy features are exposed through the web UI, not only through standalone scripts.
- README setup instructions match the committed code and compose flow.
- Backend smoke routes still pass the skeleton test.
- Schema and seed scripts in `db/init/` still load cleanly through PostgreSQL bootstrap.

## 6. Warnings and Guardrails

- Do not introduce hidden-query data layers that would violate the explicit-SQL requirement.
- Do not hardcode credentials outside `.env` or change the required grading credentials.
- Do not assume a minimum schema from the assignment; the PDF explicitly leaves schema depth and feature breadth to the student.
- Keep backend growth inside the approved domain partitions instead of dumping routes into one file.
- Keep the single Vue app split by route surface (`storefront`, `account`, `admin`) rather than creating a second frontend unless the user explicitly changes direction.

## 7. Related Docs

- Requirements source: `/Users/yehosuahercules/Downloads/Proyecto_2.pdf`
- Database draft: `/Users/yehosuahercules/Desktop/BasesDeDatos/Proyecto2-BD/diseno-bd.md`
- Scaffold plan: `/Users/yehosuahercules/Desktop/BasesDeDatos/Proyecto2-BD/docs/superpowers/plans/2026-04-19-project-foundation.md`
