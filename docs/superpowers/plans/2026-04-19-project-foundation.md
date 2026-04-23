# Project Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the approved full-stack project skeleton with the real repository layout, Docker wiring, backend domain partitions, frontend route surfaces, and initial database bootstrap files.

**Architecture:** Use a single Vue frontend, a single FastAPI backend with domain-partitioned modules, and one PostgreSQL service. Keep this phase focused on repo structure and bootstrapping, not business logic, while preserving explicit-SQL constraints and the grading credentials.

**Tech Stack:** Vue 3, Vite, Vue Router, FastAPI, psycopg, PostgreSQL, Docker Compose, pytest

---

### Task 1: Add backend skeleton smoke test

**Files:**
- Create: `backend/tests/test_app_structure.py`

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_core_health_and_domain_routes_exist():
    client = TestClient(create_app())

    expected = {
        "/health": "ok",
        "/api/auth/health": "auth",
        "/api/catalog/health": "catalog",
        "/api/orders/health": "orders",
        "/api/inventory/health": "inventory",
        "/api/reporting/health": "reporting",
        "/api/admin/health": "admin",
    }

    for path, domain in expected.items():
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["domain"] == domain
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_app_structure.py -q`
Expected: FAIL because `app.main` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create the FastAPI app factory, root router, and one router module per approved backend domain so the health endpoints exist.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_app_structure.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_app_structure.py backend/app
git commit -m "feat: scaffold backend domain skeleton"
```

### Task 2: Scaffold root runtime and database bootstrap files

**Files:**
- Create: `.env.example`
- Create: `.gitignore`
- Create: `docker-compose.yml`
- Create: `db/init/001_schema.sql`
- Create: `db/init/002_seed.sql`

- [ ] **Step 1: Add environment contract**

Define the required env variables with `POSTGRES_USER=proy2` and `POSTGRES_PASSWORD=secret`.

- [ ] **Step 2: Add compose wiring**

Create a three-service compose file for `db`, `backend`, and `frontend`, mounting the SQL init scripts into PostgreSQL.

- [ ] **Step 3: Add schema bootstrap**

Write the initial SQL schema matching the approved design at a foundational level.

- [ ] **Step 4: Add seed bootstrap**

Seed roles plus a demo admin and demo client user for grading flows.

- [ ] **Step 5: Commit**

```bash
git add .env.example .gitignore docker-compose.yml db/init
git commit -m "feat: add runtime and database foundation"
```

### Task 3: Scaffold frontend route architecture

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/views/store/HomeView.vue`
- Create: `frontend/src/views/store/CatalogView.vue`
- Create: `frontend/src/views/store/CheckoutView.vue`
- Create: `frontend/src/views/account/LoginView.vue`
- Create: `frontend/src/views/account/ProfileView.vue`
- Create: `frontend/src/views/account/OrdersView.vue`
- Create: `frontend/src/views/admin/DashboardView.vue`
- Create: `frontend/src/views/admin/ProductsView.vue`
- Create: `frontend/src/views/admin/CategoriesView.vue`
- Create: `frontend/src/views/admin/SalesView.vue`
- Create: `frontend/src/views/admin/ReportsView.vue`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Create the Vite/Vue package contract**

Add dependencies and scripts for `dev`, `build`, and `preview`.

- [ ] **Step 2: Create the route map**

Define route groups for storefront, account, and admin.

- [ ] **Step 3: Add starter views**

Create placeholder views so the architecture is visible immediately when the app boots.

- [ ] **Step 4: Add frontend container file**

Use a simple Node-based dev container for the scaffold phase.

- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "feat: scaffold frontend route surfaces"
```

### Task 4: Update repo guidance and onboarding

**Files:**
- Modify: `AGENT.md`
- Modify: `README.md`

- [ ] **Step 1: Update AGENT.md**

Replace the "repo is empty" guidance with the actual architecture, directories, and validation commands.

- [ ] **Step 2: Update README.md**

Document the new structure and the expected `docker compose up --build` flow for the foundation.

- [ ] **Step 3: Verify docs match reality**

Re-open the updated docs and ensure all paths and commands exist.

- [ ] **Step 4: Commit**

```bash
git add AGENT.md README.md
git commit -m "docs: document project foundation"
```

### Task 5: Verify the scaffold

**Files:**
- No new files required unless fixes are needed

- [ ] **Step 1: Run backend smoke test**

Run: `pytest backend/tests/test_app_structure.py -q`
Expected: PASS

- [ ] **Step 2: Run Python syntax check**

Run: `python3 -m compileall backend/app`
Expected: PASS

- [ ] **Step 3: Run JavaScript syntax checks**

Run: `node --check frontend/src/main.js frontend/src/router/index.js`
Expected: PASS

- [ ] **Step 4: Validate compose file**

Run: `docker compose config`
Expected: PASS and resolved services for `db`, `backend`, and `frontend`

- [ ] **Step 5: Commit verification-driven fixes if needed**

```bash
git add .
git commit -m "chore: fix scaffold verification issues"
```
