export const APP_ROLES = Object.freeze(["admin", "inventario", "ventas", "reportes", "cliente"]);

export const ADMIN_DASHBOARD_ROLES = Object.freeze(["admin"]);
export const INVENTORY_ROUTE_ROLES = Object.freeze(["admin", "inventario"]);
export const SALES_READ_ROLES = Object.freeze(["admin", "ventas", "reportes"]);
export const SALES_WRITE_ROLES = Object.freeze(["admin", "ventas"]);
export const REPORT_ROUTE_ROLES = Object.freeze(["admin", "inventario", "reportes"]);
export const SALES_REPORT_ROLES = Object.freeze(["admin", "reportes"]);
export const INVENTORY_REPORT_ROLES = Object.freeze(["admin", "inventario", "reportes"]);

export const BACKOFFICE_NAV_ITEMS = Object.freeze([
  { label: "Admin", to: "/admin", allowedRoles: ADMIN_DASHBOARD_ROLES },
  { label: "Productos", to: "/admin/products", allowedRoles: INVENTORY_ROUTE_ROLES },
  { label: "Categorias", to: "/admin/categories", allowedRoles: INVENTORY_ROUTE_ROLES },
  { label: "Ventas", to: "/admin/sales", allowedRoles: SALES_READ_ROLES },
  { label: "Reportes", to: "/admin/reports", allowedRoles: REPORT_ROUTE_ROLES },
]);

export function hasRole(role, allowedRoles = []) {
  return Boolean(role && allowedRoles.includes(role));
}

export function getBackofficeHomePath(role) {
  if (role === "admin") return "/admin";
  if (role === "inventario") return "/admin/products";
  if (role === "ventas") return "/admin/sales";
  if (role === "reportes") return "/admin/reports";
  return null;
}

export function getBackofficeNavItems(role) {
  return BACKOFFICE_NAV_ITEMS.filter((item) => hasRole(role, item.allowedRoles));
}
