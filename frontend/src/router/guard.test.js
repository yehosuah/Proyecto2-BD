import { describe, expect, it } from "vitest";

import { resolveGuardTarget } from "./guard";

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
    expect(resolveGuardTarget(adminRoute, session)).toEqual({ name: "forbidden" });
  });

  it("permite acceso cuando rol autorizado", () => {
    const session = { authenticated: true, user: { rol: "admin" } };
    expect(resolveGuardTarget(adminRoute, session)).toBe(true);
  });
});
