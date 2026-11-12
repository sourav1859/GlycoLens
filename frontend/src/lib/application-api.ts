import { supabase } from "./supabase";

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); this.name = "ApiError"; }
}

export async function enterDemo() {
  const connection = supabase();
  const { data } = await connection.auth.getSession();
  if (!data.session) {
    const result = await connection.auth.signInAnonymously();
    if (result.error) throw new Error("Anonymous demo access is unavailable. Sign in to use the virtual patient.");
  }
  return api("/demo/session", { method: "POST", body: JSON.stringify({}) });
}

export async function api(path: string, options: RequestInit = {}) {
  const { data } = await supabase().auth.getSession();
  if (!data.session) throw new ApiError("Sign in to continue", 401);
  const owner = data.session.user.id;
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("Authorization", `Bearer ${data.session.access_token}`);
  const base = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
  const response = await fetch(`${base}/api/v1${path}`, {
    cache: "no-store",
    ...options,
    headers,
  });
  const current = await supabase().auth.getSession();
  const deletionAcknowledged = path === "/me" && options.method === "DELETE" && response.ok && !current.data.session;
  if (current.data.session?.user.id !== owner && !deletionAcknowledged) throw new ApiError("Your account changed. Please try again.", 401);
  if (response.status === 401) await supabase().auth.signOut({ scope: "local" });
  const payload = response.status === 204 ? null : await response.json().catch(() => { throw new ApiError("The service returned an unreadable response. Please try again.", 503); });
  if (!response.ok) throw new ApiError(response.status === 409 ? "This record changed in another tab. Reload before trying again." : typeof payload?.detail === "string" ? payload.detail : "Request rejected; review your entries", response.status);
  return payload;
}
