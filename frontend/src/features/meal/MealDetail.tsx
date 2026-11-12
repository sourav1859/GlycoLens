"use client";
import Link from "next/link";
import { useRef, useState } from "react";
import { useResource } from "../../lib/use-resource";
import { api } from "../../lib/application-api";
import { displayNutrient, isMeal, nutrientFields, type Meal } from "../../lib/meal-facts";
import { AsyncState } from "../../components/ui/AsyncState";
import { AdaptiveDialog } from "../../components/ui/AdaptiveDialog";
import { PageIntro } from "../../components/layout/PageIntro";
import { useAccount } from "../auth/AccountProvider";
import { useRouter } from "next/navigation";

function valid(value:unknown):value is Meal[] {return Array.isArray(value)&&value.every(isMeal);}
export function MealDetail({id}:{id:string}) {
  const {data,error,reload}=useResource(`/meals/${id}`,valid); const [dialog,setDialog]=useState(false),[busy,setBusy]=useState(false),[failure,setFailure]=useState("");
  const {account}=useAccount();const zone=account?.preferences.timezone??"UTC";
  const cancelKey=useRef(""), forecastKey=useRef(""),router=useRouter();
  if(error)return <AsyncState title="Meal unavailable" message={error} error retry={reload}/>;
  if(!data)return <AsyncState title="Loading meal…"/>;
  const meal=data[0]; if(!meal)return <AsyncState title="Meal not found"/>;
  return <><PageIntro eyebrow={`Revision ${meal.revision} · ${meal.state}`} title={meal.name} description={`${new Date(meal.recorded_at).toLocaleString(undefined,{timeZone:zone})} · reviewed food facts`}>
    {meal.state!=="cancelled"&&<Link href={`/meals/${id}/edit`} className="button secondary">Edit meal</Link>}<Link href={`/meals/new?copy=${id}`} className="button secondary">Copy as new draft</Link></PageIntro>
    {failure&&<p role="alert" className="error-message">{failure}</p>}<section className="surface"><h2>Reviewed nutrition</h2><dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{displayNutrient(meal[f])} {f==="calories"?"kcal":"g"}</dd></div>)}</dl>
    {meal.nutrition_provenance.food_snapshots.map((f,i)=><p key={i}>{f.name??"Saved food"} · {f.grams} g · {f.source} · facts per {f.nutrient_basis_g} g</p>)}
    <p className="muted small">{meal.state==="logged"?"This revision contributes to eaten totals.":"This meal is excluded from eaten totals."} Earlier forecasts retain their original meal revision.</p>
    <div className="intro-actions"><button className="button" disabled={busy||meal.state==="cancelled"||!meal.source_session_id||nutrientFields.filter(f=>f!=="calories").some(f=>meal[f]===null)} onClick={()=>{
      setBusy(true);setFailure("");if(!forecastKey.current)forecastKey.current=crypto.randomUUID();void api("/forecasts",{method:"POST",body:JSON.stringify({meal_id:id,idempotency_key:forecastKey.current})}).then(result=>router.push(`/forecasts/${result.forecast_id}`)).catch(e=>setFailure(e instanceof Error?e.message:"Forecast unavailable")).finally(()=>setBusy(false));
    }}>{busy?"Working…":"Run selected forecast"}</button>{meal.state!=="cancelled"&&<button className="button secondary" onClick={()=>setDialog(true)}>Cancel meal</button>}</div><p className="small muted">Forecasting requires a source session and complete macro/fiber facts. Research estimates must not guide dosing or treatment.</p></section>
    <AdaptiveDialog open={dialog} onClose={()=>setDialog(false)} title="Cancel this meal?"><p>It will be removed from eaten totals. Revision history and any forecasts remain available.</p><button className="button" disabled={busy} onClick={()=>{setBusy(true);setFailure("");if(!cancelKey.current)cancelKey.current=crypto.randomUUID();void api(`/meals/${id}`,{method:"DELETE",body:JSON.stringify({revision:meal.revision,idempotency_key:cancelKey.current})}).then(()=>{setDialog(false);reload();}).catch(e=>setFailure(e instanceof Error?e.message:"Cancellation failed")).finally(()=>setBusy(false));}}>Confirm cancellation</button></AdaptiveDialog>
  </>;
}
