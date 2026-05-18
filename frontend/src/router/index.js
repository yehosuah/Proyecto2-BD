import { createRouter, createWebHistory } from "vue-router";

import { ensureSessionLoaded, sessionState } from "../stores/session";
import { resolveGuardTarget } from "./guard";
import LoginView from "../views/account/LoginView.vue";
import OrderDetailView from "../views/account/OrderDetailView.vue";
import OrdersView from "../views/account/OrdersView.vue";
import ProfileView from "../views/account/ProfileView.vue";
import RegisterView from "../views/account/RegisterView.vue";
import ForbiddenView from "../views/account/ForbiddenView.vue";
import CategoriesView from "../views/admin/CategoriesView.vue";
import DashboardView from "../views/admin/DashboardView.vue";
import ProductsView from "../views/admin/ProductsView.vue";
import ReportsView from "../views/admin/ReportsView.vue";
import SalesDetailView from "../views/admin/SalesDetailView.vue";
import SalesView from "../views/admin/SalesView.vue";
import CheckoutResultView from "../views/store/CheckoutResultView.vue";
import CheckoutView from "../views/store/CheckoutView.vue";
import CatalogView from "../views/store/CatalogView.vue";
import HomeView from "../views/store/HomeView.vue";
import ProductDetailView from "../views/store/ProductDetailView.vue";
import ForbiddenView from "../views/ForbiddenView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView, meta: { surface: "store" } },
  { path: "/catalog", name: "catalog", component: CatalogView, meta: { surface: "store" } },
  { path: "/catalog/:sku", name: "product-detail", component: ProductDetailView, meta: { surface: "store" } },
  { path: "/checkout", name: "checkout", component: CheckoutView, meta: { surface: "store" } },
  {
    path: "/checkout/resultado/:codigo",
    name: "checkout-result",
    component: CheckoutResultView,
    meta: { surface: "store" },
  },
  { path: "/account/login", name: "account-login", component: LoginView, meta: { surface: "account" } },
  { path: "/account/register", name: "account-register", component: RegisterView, meta: { surface: "account" } },
  { path: "/403", name: "forbidden", component: ForbiddenView, meta: { surface: "account" } },
  {
    path: "/account/profile",
    name: "account-profile",
    component: ProfileView,
    meta: { surface: "account", requiresAuth: true },
  },
  {
    path: "/account/orders",
    name: "account-orders",
    component: OrdersView,
    meta: { surface: "account", requiresAuth: true },
  },
  {
    path: "/account/orders/:codigo",
    name: "account-order-detail",
    component: OrderDetailView,
    meta: { surface: "account", requiresAuth: true },
  },
  {
    path: "/admin",
    name: "admin-dashboard",
    component: DashboardView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin"] },
  },
  {
    path: "/admin/products",
    name: "admin-products",
    component: ProductsView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin", "app_admin", "app_inventory"] },
  },
  {
    path: "/admin/categories",
    name: "admin-categories",
    component: CategoriesView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin", "app_admin", "app_inventory"] },
  },
  {
    path: "/admin/sales",
    name: "admin-sales",
    component: SalesView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin", "app_admin", "app_inventory"] },
  },
  {
    path: "/admin/sales/:codigo",
    name: "admin-sales-detail",
    component: SalesDetailView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin", "app_admin", "app_inventory"] },
  },
  {
    path: "/admin/reports",
    name: "admin-reports",
    component: ReportsView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ["admin", "app_admin", "app_inventory"] },
  },
  { path: "/403", name: "forbidden", component: ForbiddenView, meta: { surface: "account" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  if (!sessionState.loaded) {
    await ensureSessionLoaded();
  }
  if (to.meta.requiresAuth && !sessionState.authenticated) {
    return { name: "account-login", query: { redirect: to.fullPath } };
  }

  if (to.meta.allowedRoles?.length) {
    const role = sessionState.user?.rol;
    if (!role || !to.meta.allowedRoles.includes(role)) {
      return { name: "forbidden", query: { from: to.fullPath } };
    }
  }

  return true;
});

export default router;

