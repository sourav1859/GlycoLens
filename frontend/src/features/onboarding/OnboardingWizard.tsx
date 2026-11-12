"use client";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAccount } from "../auth/AccountProvider";
import { api, ApiError } from "../../lib/application-api";
import { Icon } from "../../components/ui/Icon";

const steps = ["preferences", "source", "optional", "review"] as const;
const labels = ["Preferences", "Data source", "Optional", "Review"];

export function OnboardingWizard() {
  const { account, applyAccount, reload, signOut } = useAccount();
  const router = useRouter();
  const [timezone, setTimezone] = useState(() => account?.onboarding.completed_steps.includes("preferences") ? account.preferences.timezone : Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC");
  const [unit, setUnit] = useState(account?.preferences.glucose_unit ?? "mg/dL");
  const [source, setSource] = useState(account?.preferences.source_mode ?? "simulation");
  const [name, setName] = useState(account?.display_name === "GlycoLens member" ? "" : account?.display_name ?? "");
  const [food, setFood] = useState(account?.preferences.food_preferences.join(", ") ?? "");
  const [ack, setAck] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [editing, setEditing] = useState<typeof steps[number] | null>(null);
  if (!account) return null;
  const step = editing ?? account.onboarding.step;
  async function submit(event: FormEvent) {
    event.preventDefault(); if (!account) return;
    setBusy(true); setError("");
    try {
      if (step === "review") {
        const value = await api("/me/onboarding/complete",{ method:"POST",body:JSON.stringify({ revision:account.onboarding.revision,notice_version:account.notice_version,acknowledged:ack }) });
        applyAccount(value); router.replace("/home");
      } else {
        const values = step === "preferences" ? { timezone,glucose_unit:unit } : step === "source" ? { source_mode:source } : { food_preferences:food.split(",").map(value => value.trim()).filter(Boolean),...(name.trim() ? { display_name:name.trim() } : {}) };
        applyAccount(await api("/me/onboarding",{ method:"PATCH",body:JSON.stringify({ revision:account.onboarding.revision,step,values }) }));
        setEditing(null);
      }
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Your progress couldn’t be saved"); if (failure instanceof ApiError && failure.status === 401) router.replace("/auth/sign-in"); }
    finally { setBusy(false); }
  }
  return <div className="onboarding-container"><p className="eyebrow">MAKE YOURSELF AT HOME</p><h1>Let’s set up your space</h1><p className="muted">A few preferences help us show the right units, dates and data. No diagnosis or body measurements required.</p><ol className="step-progress" aria-label="Onboarding progress">{steps.map((item,index) => <li key={item} aria-current={step === item ? "step" : undefined} className={account.onboarding.completed_steps.includes(item) ? "complete" : ""}>{index + 1}. {labels[index]}</li>)}</ol>
    <section className="surface"><form onSubmit={submit} aria-busy={busy}>
      {step === "preferences" && <><h2>Your app preferences</h2><p className="muted">Confirm your local timezone and glucose display unit.</p><label className="field">Timezone<input value={timezone} onChange={event => setTimezone(event.target.value)} list="common-timezones" maxLength={100} required disabled={busy} /><datalist id="common-timezones">{["UTC", "America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London", "Asia/Kolkata", "Asia/Singapore", "Australia/Sydney"].map(zone => <option key={zone} value={zone} />)}</datalist><small>Use an IANA timezone, such as Asia/Kolkata. Dates follow this timezone.</small></label><label className="field">Glucose display unit<select value={unit} onChange={event => setUnit(event.target.value as typeof unit)} disabled={busy}><option value="mg/dL">mg/dL</option><option value="mmol/L">mmol/L</option></select><small>Stored glucose values use canonical units; this changes their display.</small></label></>}
      {step === "source" && <><h2>Choose your starting data source</h2><p className="muted">This development app uses a virtual patient. Live personal CGM connections aren’t enabled.</p><label className="field">Available source<select value={source} onChange={event => setSource(event.target.value as typeof source)} disabled={busy}><option value="simulation">Virtual patient · live simulation</option><option value="replay">Virtual patient · reviewed replay</option></select><small>A reviewed replay becomes available after a scenario has run. Simulated time is labeled throughout the app.</small></label></>}
      {step === "optional" && <><h2>A little more personal</h2><p className="muted">Everything here is optional. You can leave these blank and continue.</p><label className="field">Nickname <span className="muted">Optional</span><input autoComplete="nickname" value={name} onChange={event => setName(event.target.value)} maxLength={100} disabled={busy} /></label><label className="field">Food preferences <span className="muted">Optional</span><input value={food} onChange={event => setFood(event.target.value)} placeholder="Separate short preferences with commas" maxLength={1000} disabled={busy} /><small>Preferences don’t guarantee allergen safety. Nutrition goals can be added later without an automatic calorie prescription.</small></label></>}
      {step === "review" && <><h2>Everything look right?</h2><dl className="info-list"><div><dt>Timezone</dt><dd>{account.preferences.timezone}</dd></div><div><dt>Glucose unit</dt><dd>{account.preferences.glucose_unit}</dd></div><div><dt>Data source</dt><dd>{account.preferences.source_mode === "simulation" ? "Virtual patient simulation" : "Reviewed virtual-patient replay"}</dd></div></dl><div className="form-actions"><button type="button" className="button secondary" onClick={() => setEditing("preferences")}>Edit preferences</button><button type="button" className="button secondary" onClick={() => setEditing("source")}>Edit source</button></div><p className="notice-panel">GlycoLens is a research and education application. Forecasts are uncertain estimates, not treatment or insulin-dosing advice. This flow uses simulated data and does not authorize real-patient research.</p><label className="confirmation"><input type="checkbox" checked={ack} onChange={event => setAck(event.target.checked)} required disabled={busy} />I understand the research limitations and have read the <a href="/privacy" target="_blank" rel="noopener noreferrer">development data notice (opens a new tab)</a>.</label></>}
      {error && <div className="form-error" role="alert"><p>{error}</p><button type="button" className="button secondary" onClick={() => void reload().then(() => window.location.reload()).catch(() => {})}>Reload saved progress</button></div>}
      <div className="form-actions"><button className="button" type="submit" disabled={busy || (step === "review" && !ack)}>{busy ? "Saving…" : step === "review" ? "Open my Home" : editing ? "Save changes" : step === "optional" && !name && !food ? "Skip optional details" : "Save and continue"}<Icon name="arrow" /></button><button className="button secondary" type="button" onClick={() => void signOut().then(() => router.replace("/auth/sign-in")).catch(() => setError("Sign out couldn’t complete"))} disabled={busy}>Save for later & sign out</button></div>
    </form></section><p className="small muted">Progress is saved securely after each completed step. You can return whenever you’re ready.</p></div>;
}
