const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.error?.message ?? "Request failed.";
    throw new Error(message);
  }
  return payload;
}

export async function startDebate() {
  return request("/api/v1/debates", {
    method: "POST",
    body: JSON.stringify({ mode: "automatic" }),
  });
}

export async function getDebate(debateId) {
  return request(`/api/v1/debates/${debateId}`);
}

