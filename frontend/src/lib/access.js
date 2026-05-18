import { ensureSessionLoaded, sessionState } from "../stores/session";

export function hasAllowedRole(allowedRoles = []) {
  if (!allowedRoles?.length) return true;
  const role = sessionState.user?.rol;
  return Boolean(role && allowedRoles.includes(role));
}

export async function requireRouteAccess(route, router) {
  if (!sessionState.loaded) {
    await ensureSessionLoaded();
  }

  if (route.meta?.requiresAuth && !sessionState.authenticated) {
    await router.replace({ name: "account-login", query: { redirect: route.fullPath } });
    return false;
  }

  if (!hasAllowedRole(route.meta?.allowedRoles)) {
    await router.replace({ name: "forbidden", query: { from: route.fullPath } });
    return false;
  }

  return true;
}
