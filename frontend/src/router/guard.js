export function resolveGuardTarget(to, sessionState) {
  if (to.meta?.requiresAuth && !sessionState.authenticated) {
    return { name: "account-login", query: { redirect: to.fullPath } };
  }
  if (to.meta?.allowedRoles?.length && !to.meta.allowedRoles.includes(sessionState.user?.rol)) {
    return { name: "forbidden" };
  }
  return true;
}
