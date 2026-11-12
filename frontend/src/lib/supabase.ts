import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let connection: SupabaseClient | undefined;
export function supabase() {
  if (!connection) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !key) throw new Error("The account connection is not configured");
    connection = createClient(url, key, { auth: { flowType: "pkce", persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
  }
  return connection;
}
