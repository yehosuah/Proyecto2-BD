import { createRouter, createWebHistory } from "vue-router";

import OrdersView from "../views/account/OrdersView.vue";
import LoginView from "../views/account/LoginView.vue";
import ProfileView from "../views/account/ProfileView.vue";
import CategoriesView from "../views/admin/CategoriesView.vue";
import DashboardView from "../views/admin/DashboardView.vue";
import ProductsView from "../views/admin/ProductsView.vue";
import ReportsView from "../views/admin/ReportsView.vue";
import SalesView from "../views/admin/SalesView.vue";
import CheckoutView from "../views/store/CheckoutView.vue";
import CatalogView from "../views/store/CatalogView.vue";
import HomeView from "../views/store/HomeView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView, meta: { surface: "storefront" } },
  { path: "/catalog", name: "catalog", component: CatalogView, meta: { surface: "storefront" } },
  { path: "/checkout", name: "checkout", component: CheckoutView, meta: { surface: "storefront" } },
  { path: "/account/login", name: "account-login", component: LoginView, meta: { surface: "account" } },
  { path: "/account/profile", name: "account-profile", component: ProfileView, meta: { surface: "account" } },
  { path: "/account/orders", name: "account-orders", component: OrdersView, meta: { surface: "account" } },
  { path: "/admin", name: "admin-dashboard", component: DashboardView, meta: { surface: "admin" } },
  { path: "/admin/products", name: "admin-products", component: ProductsView, meta: { surface: "admin" } },
  { path: "/admin/categories", name: "admin-categories", component: CategoriesView, meta: { surface: "admin" } },
  { path: "/admin/sales", name: "admin-sales", component: SalesView, meta: { surface: "admin" } },
  { path: "/admin/reports", name: "admin-reports", component: ReportsView, meta: { surface: "admin" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

