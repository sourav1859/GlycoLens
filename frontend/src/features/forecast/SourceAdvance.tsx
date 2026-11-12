"use client";
import { useState } from "react";
import { api } from "../../lib/application-api";
export function SourceAdvance({source,onAdvanced}:{source:{id:string;clock_at:string};onAdvanced:()=>void}) {
 const [busy,setBusy]=useState(false),[error,setError]=useState("");return <div><button className="button secondary" disabled={busy} onClick={()=>{setBusy(true);setError("");void api(`/simulation/sources/${source.id}/advance`,{method:"POST",body:JSON.stringify({minutes:120,expected_clock:source.clock_at})}).then(onAdvanced).catch(e=>setError(e instanceof Error?e.message:"Source advance unavailable")).finally(()=>setBusy(false));}}>{busy?"Advancing…":"Advance virtual clock +2 hours"}</button><p className="small muted">Reveals reviewed later observations for follow-up. Prepare a new source for another forecast origin.</p>{error&&<p role="alert">{error}</p>}</div>;
}
