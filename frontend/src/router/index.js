import { createRouter, createWebHistory } from "vue-router";

import { ensureSessionLoaded, sessionState } from "../stores/session";
import { resolveGuardTarget } from "./guard";
import { routes } from "./routes";

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  if (!sessionState.loaded) {
    await ensureSessionLoaded();
  }
  return resolveGuardTarget(to, sessionState);
});

export default router;
