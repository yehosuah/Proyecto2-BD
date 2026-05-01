import { reactive } from "vue";

import { apiRequest } from "../lib/api";

export const sessionState = reactive({
  loaded: false,
  loading: false,
  authenticated: false,
  user: null,
  error: null,
});

function applySessionPayload(payload) {
  sessionState.authenticated = payload.authenticated;
  sessionState.user = payload.user;
  sessionState.loaded = true;
}

export async function ensureSessionLoaded() {
  if (sessionState.loaded || sessionState.loading) {
    return;
  }
  sessionState.loading = true;
  try {
    const payload = await apiRequest("/api/auth/session");
    applySessionPayload(payload);
  } finally {
    sessionState.loading = false;
  }
}

export async function loginUser(credentials) {
  sessionState.loading = true;
  sessionState.error = null;
  try {
    const payload = await apiRequest("/api/auth/login", {
      method: "POST",
      body: credentials,
    });
    sessionState.authenticated = true;
    sessionState.user = payload.user;
    sessionState.loaded = true;
    return payload.user;
  } catch (error) {
    sessionState.error = error.message;
    throw error;
  } finally {
    sessionState.loading = false;
  }
}

export async function registerUser(payload) {
  sessionState.loading = true;
  sessionState.error = null;
  try {
    const response = await apiRequest("/api/auth/register", {
      method: "POST",
      body: payload,
    });
    sessionState.authenticated = true;
    sessionState.user = response.user;
    sessionState.loaded = true;
    return response.user;
  } catch (error) {
    sessionState.error = error.message;
    throw error;
  } finally {
    sessionState.loading = false;
  }
}

export async function logoutUser() {
  await apiRequest("/api/auth/logout", { method: "POST" });
  sessionState.authenticated = false;
  sessionState.user = null;
  sessionState.loaded = true;
}

