"use client";
import Link from "next/link";
import { useState, type FormEvent } from "react";
import { useAccount } from "../auth/AccountProvider";
import { api } from "../../lib/application-api";
import { PageIntro } from "../../components/layout/PageIntro";
import { Icon } from "../../components/ui/Icon";

export function AccountSettings({ profile = false }: { profile?: boolean }) {
  const { account, session, applyAccount } = useAccount();
  const [name,setName] = useState(account?.display_name ?? "");
  const [timezone,setTimezone] = useState(account?.preferences.timezone ?? "UTC");
  const [unit,setUnit] = useState(account?.preferences.glucose_unit ?? "mg/dL");
  const [source,setSource] = useState(account?.preferences.source_mode ?? "simulation");
  const [busy,setBusy] = useState(false), [error,setError] = useState(""), [notice,setNotice] = useState("");
  if (!account) return null;
  async function save(event: FormEvent) {
    event.preventDefault(); if (!account) return;
    setBusy(true); setError(""); setNotice("");
    try { applyAccount(await api("/me/preferences",{method:"PATCH",body:JSON.stringify({revision:account.preferences.revision,display_name:name,timezone,glucose_unit:unit,source_mode:source})})); setNotice("Your preferences have been saved."); }
    catch (failure) { setError(failure instanceof Error ? failure.message : "Preferences couldn’t be saved"); }
    finally { setBusy(false); }
  }
  return <><PageIntro eyebrow="YOUR SPACE" title={profile ? "Your profile" : "Your preferences"} description="Keep your account and display choices up to date."><Link className="button secondary" href="/settings/privacy">Data controls</Link><Link className="button secondary" href="/settings/connections">Connections</Link></PageIntro>{error && <p className="form-error" role="alert">{error}</p>}{notice && <p className="notice-panel" role="status">{notice}</p>}
    <div className="dashboard-grid"><section className="surface">{profile ? <><span className="icon-tile large"><Icon name="profile" /></span><h2>{account.display_name}</h2><dl className="info-list"><div><dt>Email</dt><dd>{session?.user.email ?? "Anonymous demonstration"}</dd></div><div><dt>Timezone</dt><dd>{account.preferences.timezone}</dd></div><div><dt>Glucose unit</dt><dd>{account.preferences.glucose_unit}</dd></div><div><dt>Source</dt><dd>{account.preferences.source_mode === "simulation" ? "Virtual patient simulation" : "Reviewed replay"}</dd></div></dl><div className="form-actions"><Link className="button" href="/settings">Edit preferences</Link></div></> : <form onSubmit={save} aria-busy={busy}><h2>Display & app preferences</h2><label className="field">Display name<input value={name} onChange={event=>setName(event.target.value)} required maxLength={100} disabled={busy}/></label><label className="field">Timezone<input value={timezone} onChange={event=>setTimezone(event.target.value)} required maxLength={100} disabled={busy}/><small>Use an IANA timezone. Your local-day totals will be regrouped without changing saved timestamps.</small></label><div className="form-grid"><label className="field">Glucose display unit<select value={unit} onChange={event=>setUnit(event.target.value as typeof unit)} disabled={busy}><option value="mg/dL">mg/dL</option><option value="mmol/L">mmol/L</option></select></label><label className="field">Data-source preference<select value={source} onChange={event=>setSource(event.target.value as typeof source)} disabled={busy}><option value="simulation">Virtual patient simulation</option><option value="replay">Reviewed replay</option></select></label></div><button className="button" disabled={busy}>{busy ? "Saving…" : "Save preferences"}</button></form>}</section><aside className="surface"><h2>Your account controls</h2><p className="muted">Permanent credentials are managed by Supabase Auth. No passwords are stored in the application tables.</p><div className="quick-add-options"><Link href="/favorites"><Icon name="heart"/><span>Your favorites</span><Icon name="arrow"/></Link><Link href="/privacy"><Icon name="help"/><span>Development data notice</span><Icon name="arrow"/></Link><Link href="/help"><Icon name="help"/><span>Help & research limitations</span><Icon name="arrow"/></Link></div><p className="notice-panel">You can export your own application records from Data controls. Data controls also let you permanently delete your account after password verification and explicit confirmation, with no recovery window.</p></aside></div></>;
}
