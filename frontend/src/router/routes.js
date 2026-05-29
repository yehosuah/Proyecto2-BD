import LoginView from "../views/account/LoginView.vue";
import OrderDetailView from "../views/account/OrderDetailView.vue";
import OrdersView from "../views/account/OrdersView.vue";
import ProfileView from "../views/account/ProfileView.vue";
import RegisterView from "../views/account/RegisterView.vue";
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

import {
  ADMIN_DASHBOARD_ROLES,
  INVENTORY_ROUTE_ROLES,
  REPORT_ROUTE_ROLES,
  SALES_READ_ROLES,
} from "../lib/roles";

export const routes = [
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
    meta: { surface: "admin", requiresAuth: true, allowedRoles: ADMIN_DASHBOARD_ROLES },
  },
  {
    path: "/admin/products",
    name: "admin-products",
    component: ProductsView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: INVENTORY_ROUTE_ROLES },
  },
  {
    path: "/admin/categories",
    name: "admin-categories",
    component: CategoriesView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: INVENTORY_ROUTE_ROLES },
  },
  {
    path: "/admin/sales",
    name: "admin-sales",
    component: SalesView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: SALES_READ_ROLES },
  },
  {
    path: "/admin/sales/:codigo",
    name: "admin-sales-detail",
    component: SalesDetailView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: SALES_READ_ROLES },
  },
  {
    path: "/admin/reports",
    name: "admin-reports",
    component: ReportsView,
    meta: { surface: "admin", requiresAuth: true, allowedRoles: REPORT_ROUTE_ROLES },
  },
];
