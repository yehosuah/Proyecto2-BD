const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function withQuery(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      search.set(key, value);
    }
  });
  const query = search.toString();
  return `${API_BASE}${path}${query ? `?${query}` : ""}`;
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

export async function apiRequest(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const method = options.method || "GET";
  const shouldSendJsonHeader = !isFormData && !["GET", "HEAD"].includes(method.toUpperCase());
  const response = await fetch(withQuery(path, options.params), {
    method,
    credentials: "include",
    headers: {
      ...(shouldSendJsonHeader ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    body:
      options.body === undefined || options.body === null || isFormData
        ? options.body
        : JSON.stringify(options.body),
  });

  const payload = await parseResponse(response);
  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? payload.detail
        : payload;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

export function apiFileUrl(path, params = {}) {
  return withQuery(path, params);
}
