"use client";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { usePathname, useRouter } from "next/navigation";
import { supabase } from "../../lib/supabase";
import { api } from "../../lib/application-api";
import { isAccount, type Account } from "../../lib/account";
import { AsyncState } from "../../components/ui/AsyncState";

type State = { session: Session | null; account: Account | null; initializing: boolean; error: string; recovery: boolean; applyAccount: (value: unknown) => void; reload: () => Promise<void>; signOut: () => Promise<void>; clearDeletedAccount: (owner: string) => Promise<void> };
const Context = createContext<State | null>(null);

export function AccountProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [account, setAccount] = useState<Account | null>(null);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState("");
  const [recovery, setRecovery] = useState(false);
  const userId = session?.user.id;
  useEffect(() => {
    let active = true;
    try {
      const connection = supabase();
      const { data: listener } = connection.auth.onAuthStateChange((event, next) => {
        if (!active) return;
        setSession(next); setInitializing(false);
        if (!next) { setAccount(null); setError(""); setRecovery(false); }
        if (event === "PASSWORD_RECOVERY") setRecovery(true);
      });
      void connection.auth.getSession().then(({ data, error: failure }) => {
        if (active) { setSession(data.session); setInitializing(false); if (failure) setError("The account connection is unavailable"); }
      });
      return () => { active = false; listener.subscription.unsubscribe(); };
    } catch { queueMicrotask(() => { if (active) { setError("The account connection is not configured"); setInitializing(false); } }); }
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!userId) return;
    let active = true;
    void api("/me/bootstrap", { method: "POST", body: "{}" }).then(value => {
      if (!isAccount(value)) throw new Error("Account data failed validation");
      if (active && value.user_id === userId) { setAccount(value); setError(""); }
    }).catch(() => { if (active) setError("We couldn’t load your account. Your saved records haven’t changed."); });
    return () => { active = false; };
  }, [userId]);
  const visibleAccount = account?.user_id === userId ? account : null;
  function applyAccount(value: unknown) {
    if (!isAccount(value) || value.user_id !== userId) throw new Error("Account data failed validation");
    setAccount(value); setError("");
  }
  async function reload() { applyAccount(await api("/me/bootstrap", { method: "POST", body: "{}" })); }
  async function signOut() {
    const { error: failure } = await supabase().auth.signOut();
    if (failure) throw new Error("Sign out couldn’t complete. Please try again.");
    setAccount(null); setSession(null); setError("");
  }
  async function clearDeletedAccount(owner: string) {
    const connection = supabase();
    const current = await connection.auth.getSession();
    if (current.data.session && current.data.session.user.id !== owner) throw new Error("Your account changed. Sign out before continuing.");
    const { error: failure } = await connection.auth.signOut({ scope: "local" });
    // The installed SDK removes local credentials even when remote logout fails.
    // A confirmed deletion must still reach its outcome page once storage is clear.
    const after = await connection.auth.getSession();
    if (failure && after.data.session) throw new Error("Your account was deleted. Close this window and sign out to clear this browser.");
    setAccount(null); setSession(null); setError(""); setRecovery(false);
  }
  return <Context.Provider value={{ session, account: visibleAccount, initializing, error, recovery, applyAccount, reload, signOut, clearDeletedAccount }}>{children}</Context.Provider>;
}

export function useAccount() { const state = useContext(Context); if (!state) throw new Error("Account provider missing"); return state; }

export function AccountGate({ children }: { children: ReactNode }) {
  const { session, account, initializing, error, reload } = useAccount();
  const path = usePathname(), router = useRouter();
  useEffect(() => {
    if (initializing) return;
    if (!session) router.replace("/auth/sign-in?next=" + encodeURIComponent(path));
    else if (account && !account.onboarding.completed_at && path !== "/onboarding") router.replace("/onboarding");
    else if (account?.onboarding.completed_at && path === "/onboarding") router.replace("/home");
  }, [session, account, initializing, path, router]);
  if (error) return <main className="public-main"><AsyncState title="Your account is temporarily unavailable" message={error} error retry={() => void reload().catch(() => {})} /></main>;
  if (initializing || !session || !account || (!account.onboarding.completed_at && path !== "/onboarding") || (account.onboarding.completed_at && path === "/onboarding")) return <main className="public-main"><AsyncState title="Opening your space…" /></main>;
  return <div key={`${account.user_id}:${account.preferences.source_mode}:${account.preferences.source_session_id ?? "none"}`}>{children}</div>;
}
