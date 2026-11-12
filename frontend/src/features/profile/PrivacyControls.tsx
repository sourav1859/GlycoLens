"use client";
import { useState, type FormEvent } from "react";
import { api } from "../../lib/application-api";
import { PageIntro } from "../../components/layout/PageIntro";
import { useAccount } from "../auth/AccountProvider";

export function PrivacyControls() {
  const { account, session, clearDeletedAccount } = useAccount();
  const unavailable = session?.user.is_anonymous
    ? "This password-confirmed flow requires an email/password account. Anonymous demo deletion is not supported yet. Signing out loses access to that demo identity."
    : session?.user.factors?.some(factor => factor.status === "verified")
      ? "This account uses MFA. Permanent deletion requires a supported fresh MFA challenge, which is not available yet."
      : "";
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [expanded, setExpanded] = useState(false), [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState(""), [understood, setUnderstood] = useState(false);
  async function download() {
    setBusy(true); setError("");
    try {
      const value = await api("/me/export");
      const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }));
      const anchor = document.createElement("a"); anchor.href = url; anchor.download = "glycolens-export.json"; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Export unavailable"); }
    finally { setBusy(false); }
  }
  async function remove(event: FormEvent) {
    event.preventDefault();
    if (!account || !understood || confirmation !== "DELETE") return;
    const owner = account.user_id;
    setBusy(true); setError("");
    try {
      const result = await api("/me", { method: "DELETE", body: JSON.stringify({ password, confirmation }) });
      if (result?.deleted !== true || typeof result.file_cleanup_pending !== "boolean") throw new Error("Deletion could not be confirmed. Sign in again to check your account.");
      await clearDeletedAccount(owner);
      window.location.replace("/account-deleted" + (result.file_cleanup_pending ? "?cleanup=pending" : ""));
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Deletion could not be confirmed"); setBusy(false); }
    finally { setPassword(""); }
  }
  return <>
    <PageIntro title="Your data controls" description="Manage your application records. Keep exported files private." />
    {error && <p role="alert" className="form-error">{error}</p>}
    <section className="surface"><h2>Account export</h2><p>Includes preferences, onboarding acknowledgements, source data, reviewed meals, frozen forecasts and application activity. Auth passwords, tokens and API credentials are excluded. The development export limit is 5,000 records.</p><button className="button" disabled={busy} onClick={() => void download()}>{busy ? "Please wait…" : "Download my records"}</button></section>
    <section className="surface"><h2>Delete your account permanently</h2><p>Your account, meals, forecasts, source records, settings and notifications will be deleted immediately after your password and confirmation are verified. There is no recovery window. Download any records you want to keep first.</p><p className="muted">Private source files are removed with automatic retries if storage is unavailable. Provider backups and security logs follow provider retention; this action cannot instantly erase those copies. Files you downloaded remain under your control.</p>
      {unavailable ? <p className="notice-panel">{unavailable}</p> : !expanded ? <button className="button secondary" disabled={busy} onClick={() => setExpanded(true)}>Review account deletion</button> :
        <form onSubmit={remove} aria-busy={busy}>
          <label className="field">Current password<input type="password" autoComplete="current-password" required maxLength={128} value={password} onChange={event => setPassword(event.target.value)} disabled={busy} /></label>
          <label className="field">Type DELETE to confirm<input autoComplete="off" spellCheck={false} required value={confirmation} onChange={event => setConfirmation(event.target.value)} disabled={busy} /></label>
          <label className="check-field"><input type="checkbox" checked={understood} onChange={event => setUnderstood(event.target.checked)} disabled={busy} />I understand this permanently deletes my account with no recovery window.</label>
          <div className="form-actions"><button className="button danger" disabled={busy || !password || confirmation !== "DELETE" || !understood}>{busy ? "Deleting account…" : "Permanently delete my account"}</button><button className="button secondary" type="button" disabled={busy} onClick={() => { setExpanded(false); setPassword(""); setConfirmation(""); setUnderstood(false); }}>Cancel</button></div>
        </form>}
    </section>
  </>;
}
