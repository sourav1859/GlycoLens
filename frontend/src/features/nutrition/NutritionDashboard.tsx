"use client";
import Link from "next/link";
import { useState } from "react";
import { useResource } from "../../lib/use-resource";
import { api } from "../../lib/application-api";
import { displayNutrient, nutrientFields } from "../../lib/meal-facts";
import { isNutritionSummary, type Summary } from "../../lib/nutrition";
import { useAccount } from "../auth/AccountProvider";
import { MealRows } from "../meal/MealHistory";
import { PageIntro } from "../../components/layout/PageIntro";
import { AsyncState } from "../../components/ui/AsyncState";
import { SourceAdvance } from "../forecast/SourceAdvance";
import { SavedForecast } from "../forecast/SavedForecast";

export function NutritionDashboard({home=false}:{home?:boolean}) {
  const [day,setDay]=useState(""),[busy,setBusy]=useState(""),[failure,setFailure]=useState("");const {account,reload:reloadAccount}=useAccount();
  const {data,error,reload}=useResource<Summary>(`${home?"/home":"/nutrition"}${day?`?day=${day}`:""}`,isNutritionSummary);
  async function prepare(replay:boolean) {setBusy("Preparing virtual source…");setFailure("");try{await api("/simulation/scenario",{method:"POST",body:JSON.stringify({replay})});await reloadAccount();reload();}catch(e){setFailure(e instanceof Error?e.message:"Source unavailable");}finally{setBusy("");}}
  const selected=data?.days.find(d=>d.day===(day||data.day)), glucose=data?.latest_glucose?.[0];
  return <><PageIntro eyebrow={home?"Your daily overview":"Reviewed eaten meals"} title={home?`Hello, ${account?.display_name??"there"}`:"Nutrition"} description="Virtual-patient research data. Only confirmed eaten meals contribute to these totals."><Link className="button" href="/meals/new">Add a meal</Link>{data?.source&&<SourceAdvance source={data.source} onAdvanced={reload}/>}</PageIntro>
    {failure&&<p role="alert" className="error-message">{failure}</p>}{error?<AsyncState title="Daily data unavailable" message={error} error retry={reload}/>:!data?<AsyncState title="Loading your day…"/>:<>
    <section className="surface"><div className="surface-heading"><div><h2>Source and clock</h2><p className="muted">{data.source?`${data.source.mode} · ${new Date(data.source.clock_at).toLocaleString(undefined,{timeZone:data.timezone})} (${data.timezone})`:"No source context prepared"}</p></div>{glucose&&<strong>{(Number(glucose.glucose_mg_dl)/(account?.preferences.glucose_unit==="mmol/L"?18.0182:1)).toFixed(account?.preferences.glucose_unit==="mmol/L"?1:0)} {account?.preferences.glucose_unit}</strong>}</div><div className="intro-actions"><button className="button secondary" disabled={!!busy} onClick={()=>void prepare(false)}>Run virtual patient</button><button className="button secondary" disabled={!!busy} onClick={()=>void prepare(true)}>Use reviewed replay</button></div><p role="status" className="small muted">{busy||"A new run creates a separate source session. Existing meals and forecasts retain their original context."}</p></section>
    {!data.available?<section className="surface empty-panel"><h2>Prepare your first source</h2><p>Nutrition and glucose values will appear when reviewed source data is available.</p></section>:<>
    {home&&data.forecasts?.[0]&&<SavedForecast id={data.forecasts[0].id} compact/>}
    <section className="surface"><div className="surface-heading"><h2>{home?"Eaten today":"Daily nutrition"}</h2><label>Local day<input type="date" value={day||data.day||""} onChange={e=>setDay(e.target.value)}/></label></div><p className="muted small">{selected?.meal_count??0} eaten meals · {data.timezone}. Planned/cancelled meals, copies and scenarios are excluded.</p><dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{displayNutrient(selected?.nutrients[f].total)} {f==="calories"?"kcal":"g"}</dd>{!!selected?.nutrients[f].missing_meals&&<span className="small muted">{selected.nutrients[f].missing_meals} meal(s) missing facts</span>}</div>)}</dl>
    {data.goals.length?data.goals.map(g=><p className="small muted" key={g.nutrient}>Your {g.nutrient.replace("_g","")} target: {g.target} {g.unit} (from {g.effective_date})</p>):<p className="small muted">No nutrition targets set. GlycoLens does not prescribe calorie or nutrient goals.</p>}</section>
    {!home&&<section className="surface"><h2>Seven-day overview</h2><div className="table-scroll" role="region" aria-label="Data table; scroll horizontally for all columns" tabIndex={0}><table><caption>Consumed nutrition in {data.timezone}; unknown means incomplete facts</caption><thead><tr><th>Local day</th><th>Meals</th>{nutrientFields.map(f=><th key={f}>{f.replace("_g","")} ({f==="calories"?"kcal":"g"})</th>)}</tr></thead><tbody>{data.days.map(d=><tr key={d.day}><th>{d.day}</th><td>{d.meal_count}</td>{nutrientFields.map(f=><td key={f}>{displayNutrient(d.nutrients[f].total)}</td>)}</tr>)}</tbody></table></div></section>}
    <section className="surface"><div className="surface-heading"><h2>Eaten meals</h2><Link className="button secondary compact" href="/meals">All meal history</Link></div>{data.meals.length?<MealRows meals={data.meals}/>:<p className="muted">No eaten meals recorded for this local day.</p>}</section>
    {home&&<section className="surface"><h2>Recipes and products</h2><p className="muted">The corrected catalog is awaiting validation. You can use provider food facts while adding a meal.</p><Link className="button secondary" href="/search">Catalog status</Link></section>}</>}
    </>}
  </>;
}
