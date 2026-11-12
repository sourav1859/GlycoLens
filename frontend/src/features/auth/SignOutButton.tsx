"use client";
import { useState } from "react";
import { useAccount } from "./AccountProvider";
import { supabase } from "../../lib/supabase";
import { Icon } from "../../components/ui/Icon";

export function SignOutButton() {
  const { session, signOut } = useAccount();
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  if (!session) return null;
  async function logout() {
    if (busy) return;
    if (session?.user.is_anonymous && !window.confirm("Signing out of an anonymous demo loses access to that demo identity. Continue?")) return;
    setBusy(true); setError("");
    try {
      await signOut();
      // A full navigation also discards in-flight UI work and unsaved private drafts.
      window.location.replace("/auth/sign-in");
    } catch {
      const { data } = await supabase().auth.getSession();
      if (!data.session) window.location.replace("/auth/sign-in");
      else { setError("Sign out couldn’t complete. Please try again."); setBusy(false); }
    }
  }
  return <span className="sign-out-control"><button className="button secondary compact" type="button" onClick={() => void logout()} disabled={busy}><Icon name="logout" />{busy ? "Signing out…" : "Sign out"}</button>{error && <span className="form-error" role="alert">{error}</span>}</span>;
}
