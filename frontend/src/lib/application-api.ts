import { createClient, SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | undefined;

function supabase() {
  if (!client) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !key) throw new Error("Local demo session is not configured");
    client = createClient(url, key);
  }
  return client;
}

export async function enterDemo() {
  const connection = supabase();
  const { data } = await connection.auth.getSession();
  if (!data.session) {
    const result = await connection.auth.signInAnonymously();
    if (result.error) throw new Error("Demo sign-in is unavailable; check the local Auth setup");
  }
  return api("/demo/session", { method: "POST", body: JSON.stringify({}) });
}

export async function api(path: string, options: RequestInit = {}) {
  const { data } = await supabase().auth.getSession();
  if (!data.session) throw new Error("Enter demo mode first");
  const base = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
  const response = await fetch(`${base}/api/v1${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${data.session.access_token}` },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Request rejected; review your entries");
  return payload;
}
