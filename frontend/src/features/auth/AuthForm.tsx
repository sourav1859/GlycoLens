"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Brand } from "../../components/layout/AppShell";
import { Icon } from "../../components/ui/Icon";
import { emailDeliveryEnabled, passwordIsValid, safeReturnPath } from "../../lib/auth-policy";
import { supabase } from "../../lib/supabase";
import { useAccount } from "./AccountProvider";

type Mode = "sign-in" | "sign-up" | "forgot-password" | "reset-password";
const titles: Record<Mode,string> = { "sign-in":"Welcome back", "sign-up":"A clearer view starts here", "forgot-password":"Reset your password", "reset-password":"Choose a new password" };

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const { session, recovery } = useAccount();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const anonymous = session?.user.is_anonymous && mode === "sign-up";
  const emailUnavailable = mode === "forgot-password" && !emailDeliveryEnabled;
  const invalidRecovery = mode === "reset-password" && (!session || !recovery);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setNotice(""); setBusy(true);
    try {
      const connection = supabase();
      if (mode !== "sign-in" && mode !== "forgot-password" && !passwordIsValid(password)) throw new Error("Use a password or passphrase with 12–128 characters.");
      if (mode === "sign-in") {
        const { error: failure } = await connection.auth.signInWithPassword({ email, password });
        if (failure) throw new Error("We couldn’t sign you in. Check your details and try again shortly.");
        setPassword(""); router.replace(safeReturnPath(new URLSearchParams(window.location.search).get("next")));
      } else if (mode === "sign-up") {
        if (anonymous) throw new Error("Your demo identity must be kept separate until verified account linking is available.");
        const { data, error: failure } = await connection.auth.signUp({ email, password, options:{ emailRedirectTo:window.location.origin + "/auth/callback" } });
        if (failure) throw new Error("We couldn’t create the account. Try signing in or try again shortly.");
        setPassword(""); router.replace(data.session ? "/onboarding" : "/auth/check-email");
      } else if (mode === "forgot-password") {
        if (!emailDeliveryEnabled) throw new Error("Email recovery is not enabled for this development environment.");
        const { error: failure } = await connection.auth.resetPasswordForEmail(email, { redirectTo:window.location.origin + "/auth/callback" });
        if (failure) throw new Error("The request couldn’t be completed. Please try again shortly.");
        setNotice("If an eligible account exists, a recovery email will be sent. Check your inbox.");
      } else {
        if (!session || !recovery) throw new Error("Open a valid password recovery link to continue.");
        const { error: failure } = await connection.auth.updateUser({ password });
        if (failure) throw new Error("The password couldn’t be changed. Request a fresh recovery link.");
        setPassword(""); await connection.auth.signOut(); router.replace("/auth/sign-in");
      }
    } catch (failure) { setError(failure instanceof Error ? failure.message : "The request couldn’t be completed"); }
    finally { setBusy(false); }
  }
  return <div className="auth-page"><aside className="auth-story"><Link href="/" className="brand-link" style={{padding:0,color:"inherit",textDecoration:"none"}}><Brand /></Link><div><p className="eyebrow" style={{color:"#c9e8d5"}}>MEALS. CONTEXT. UNDERSTANDING.</p><h1>Small moments.<br />A clearer picture.</h1><p>Bring reviewed food facts and uncertain glucose forecasts together, one meal at a time.</p></div><p className="small">Research and education only. Never use a forecast to change insulin or treatment.</p></aside><main className="auth-form-wrap"><div className="auth-card"><Link href="/" aria-label="GlycoLens welcome" style={{color:"inherit",textDecoration:"none"}}><Brand /></Link><h1>{titles[mode]}</h1><p className="muted">{mode === "sign-in" ? "Sign in to return to your meals and preferences." : mode === "sign-up" ? "Create your account, then choose a few simple app preferences." : "Your account credentials are managed by Supabase Auth."}</p>
    {!emailDeliveryEnabled && <p className="notice-panel">Development environment: email verification and delivery are currently deferred. Use synthetic account information while testing.</p>}
    {anonymous && <p className="notice-panel">An anonymous demo is active. Its records stay with that identity; creating another account will not transfer them by email. Verified account linking will be available after email setup.</p>}
    {emailUnavailable && <p className="notice-panel">Password recovery email isn’t configured yet. This flow will be enabled after delivery is configured and tested.</p>}
    {invalidRecovery && <p className="notice-panel">This isn’t an active recovery session. Request a new recovery link when email delivery is available.</p>}
    {error && <p className="form-error" role="alert">{error}</p>}{notice && <p className="notice-panel" role="status">{notice}</p>}
    <form onSubmit={submit} aria-busy={busy}>
      {mode !== "reset-password" && <label className="field">Email address<input type="email" autoComplete="email" required maxLength={254} value={email} onChange={event => setEmail(event.target.value)} disabled={busy || emailUnavailable || !!anonymous} /></label>}
      {mode !== "forgot-password" && <label className="field">{mode === "reset-password" ? "New password" : "Password"}<input type="password" autoComplete={mode === "sign-in" ? "current-password" : "new-password"} required minLength={mode === "sign-in" ? 1 : 12} maxLength={128} value={password} onChange={event => setPassword(event.target.value)} disabled={busy || invalidRecovery || !!anonymous} />{mode !== "sign-in" && <small>Use 12–128 characters. A memorable passphrase works well.</small>}</label>}
      {mode === "sign-in" && <p className="small" style={{textAlign:"right"}}><Link className="text-link" href="/auth/forgot-password">Forgot password?</Link></p>}
      <button className="button" type="submit" disabled={busy || emailUnavailable || invalidRecovery || !!anonymous}>{busy ? "Please wait…" : mode === "sign-in" ? "Sign in" : mode === "sign-up" ? "Create account" : mode === "forgot-password" ? "Request reset link" : "Save new password"}<Icon name="arrow" /></button>
    </form><p className="small muted" style={{textAlign:"center",marginTop:24}}>{mode === "sign-in" ? <>New to GlycoLens? <Link className="text-link" href="/auth/sign-up">Create an account</Link></> : <Link className="text-link" href="/auth/sign-in">Back to sign in</Link>}</p><p className="small muted" style={{textAlign:"center"}}><Link className="text-link" href="/privacy">Development data notice</Link> · <Link className="text-link" href="/help">Help</Link></p></div></main></div>;
}
