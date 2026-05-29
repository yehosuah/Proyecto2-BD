import { describe, expect, it } from "vitest";

import {
  ADMIN_DASHBOARD_ROLES,
  APP_ROLES,
  INVENTORY_ROUTE_ROLES,
  REPORT_ROUTE_ROLES,
  SALES_READ_ROLES,
} from "../lib/roles";
import { resolveGuardTarget } from "./guard";

const routeFixtures = {
  catalog: { path: "/catalog", meta: { surface: "store" } },
  checkout: { path: "/checkout", meta: { surface: "store" } },
  accountProfile: { path: "/account/profile", meta: { surface: "account", requiresAuth: true } },
  adminDashboard: { path: "/admin", meta: { surface: "admin", requiresAuth: true, allowedRoles: ADMIN_DASHBOARD_ROLES } },
  adminProducts: { path: "/admin/products", meta: { surface: "admin", requiresAuth: true, allowedRoles: INVENTORY_ROUTE_ROLES } },
  adminCategories: { path: "/admin/categories", meta: { surface: "admin", requiresAuth: true, allowedRoles: INVENTORY_ROUTE_ROLES } },
  adminSales: { path: "/admin/sales", meta: { surface: "admin", requiresAuth: true, allowedRoles: SALES_READ_ROLES } },
  adminSalesDetail: { path: "/admin/sales/ABC123", meta: { surface: "admin", requiresAuth: true, allowedRoles: SALES_READ_ROLES } },
  adminReports: { path: "/admin/reports", meta: { surface: "admin", requiresAuth: true, allowedRoles: REPORT_ROUTE_ROLES } },
};

function authSession(role) {
  return { authenticated: true, user: { rol: role } };
}

function guardRoute(route) {
  return { ...route, fullPath: route.path };
}

function forbidden(route) {
  return { name: "forbidden", query: { from: route.path } };
}

function expectRoleMatrix(routeName, allowedRoles) {
  const route = routeFixtures[routeName];
  expect(route).toBeTruthy();

  for (const role of APP_ROLES) {
    const expected = allowedRoles.includes(role) ? true : forbidden(route);
    expect(resolveGuardTarget(guardRoute(route), authSession(role))).toEqual(expected);
  }
}

describe("resolveGuardTarget", () => {
  const adminRoute = {
    fullPath: "/admin/products",
    meta: { requiresAuth: true, allowedRoles: ["admin"] },
  };

  it("redirige a login cuando no autenticado", () => {
    const session = { authenticated: false, user: null };
    expect(resolveGuardTarget(adminRoute, session)).toEqual({
      name: "account-login",
      query: { redirect: "/admin/products" },
    });
  });

  it("redirige a 403 cuando autenticado sin permisos", () => {
    const session = { authenticated: true, user: { rol: "cliente" } };
    expect(resolveGuardTarget(adminRoute, session)).toEqual({
      name: "forbidden",
      query: { from: "/admin/products" },
    });
  });

  it("permite acceso cuando rol autorizado", () => {
    const session = { authenticated: true, user: { rol: "admin" } };
    expect(resolveGuardTarget(adminRoute, session)).toBe(true);
  });

  it("mantiene catalogo y checkout publicos", () => {
    const guest = { authenticated: false, user: null };

    expect(resolveGuardTarget(guardRoute(routeFixtures.catalog), guest)).toBe(true);
    expect(resolveGuardTarget(guardRoute(routeFixtures.checkout), guest)).toBe(true);
  });

  it("requiere sesion para paginas de cuenta sin limitar el rol autenticado", () => {
    const route = routeFixtures.accountProfile;

    expect(resolveGuardTarget(guardRoute(route), { authenticated: false, user: null })).toEqual({
      name: "account-login",
      query: { redirect: "/account/profile" },
    });

    for (const role of APP_ROLES) {
      expect(resolveGuardTarget(guardRoute(route), authSession(role))).toBe(true);
    }
  });

  it("limita rutas admin a los cinco roles de aplicacion", () => {
    const allowedRoles = Object.values(routeFixtures).flatMap((route) => route.meta?.allowedRoles || []);

    expect(allowedRoles).not.toContain("app_admin");
    expect(allowedRoles).not.toContain("app_inventory");
    expect(new Set(allowedRoles)).toEqual(new Set(["admin", "inventario", "ventas", "reportes"]));
  });

  it("protege dashboard solo para admin", () => {
    expectRoleMatrix("adminDashboard", ["admin"]);
  });

  it("protege inventario para admin e inventario", () => {
    expectRoleMatrix("adminProducts", ["admin", "inventario"]);
    expectRoleMatrix("adminCategories", ["admin", "inventario"]);
  });

  it("protege ventas para admin, ventas y reportes", () => {
    expectRoleMatrix("adminSales", ["admin", "ventas", "reportes"]);
    expectRoleMatrix("adminSalesDetail", ["admin", "ventas", "reportes"]);
  });

  it("protege reportes para admin, inventario y reportes", () => {
    expectRoleMatrix("adminReports", ["admin", "inventario", "reportes"]);
  });
});
