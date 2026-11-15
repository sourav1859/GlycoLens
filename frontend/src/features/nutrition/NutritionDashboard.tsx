"use client";
import Link from "next/link";
import { useState } from "react";
import { useResource } from "../../lib/use-resource";
import { displayNutrient, nutrientFields } from "../../lib/meal-facts";
import { isNutritionSummary, type Summary } from "../../lib/nutrition";
import { useAccount } from "../auth/AccountProvider";
import { MealRows } from "../meal/MealHistory";
import { PageIntro } from "../../components/layout/PageIntro";
import { AsyncState } from "../../components/ui/AsyncState";
import { usePersonalClock } from "../../lib/personal-clock";

function personalSummary(value:unknown):value is Summary{return isNutritionSummary(value)&&value.workspace==="personal"&&value.source===null&&value.meals.every(m=>m.workspace==="personal");}

export function NutritionDashboard({home=false}:{home?:boolean}) {
  const [day,setDay]=useState(""); const {account}=useAccount();
  const clock=usePersonalClock(account?.preferences.timezone??"UTC");
  const {data,error,reload}=useResource<Summary>(`${home?"/home":"/nutrition"}${day?`?day=${day}`:""}`,personalSummary,clock.day);
  const selected=data?.days.find(d=>d.day===(day||data.day));
  return <><PageIntro eyebrow={home?"Your daily overview":"Reviewed eaten meals"} title={home?`Hello, ${account?.display_name??"there"}`:"Nutrition"} description="Your personal meal log. Only confirmed eaten meals contribute to these totals."><Link className="button" href="/meals/new">Add a meal</Link></PageIntro>
    {error?<AsyncState title="Daily data unavailable" message={error} error retry={reload}/>:!data?<AsyncState title="Loading your day…"/>:<>
    <section className="surface"><h2>Your local time</h2><p>{clock.now?.toLocaleString(undefined,{timeZone:data.timezone})??"Loading current time…"} ({data.timezone})</p><p className="muted">No personal glucose source is connected. You can log meals and review nutrition without one.</p><Link className="button secondary" href="/demo">Open virtual simulation</Link></section>
    <section className="surface"><div className="surface-heading"><h2>{day?"Eaten on selected day":home?"Eaten today":"Daily nutrition"}</h2><label>Local day<input type="date" value={day||data.day||""} onChange={e=>setDay(e.target.value)}/></label></div><p className="muted small">{selected?.meal_count??0} eaten meals · {data.timezone}. Planned/cancelled meals, copies and scenarios are excluded.</p><dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{displayNutrient(selected?.nutrients[f].total)} {f==="calories"?"kcal":"g"}</dd>{!!selected?.nutrients[f].missing_meals&&<span className="small muted">{selected.nutrients[f].missing_meals} meal(s) missing facts</span>}</div>)}</dl>
    {data.goals.length?data.goals.map(g=><p className="small muted" key={g.nutrient}>Your {g.nutrient.replace("_g","")} target: {g.target} {g.unit} (from {g.effective_date})</p>):<p className="small muted">No nutrition targets set. GlycoLens does not prescribe calorie or nutrient goals.</p>}</section>
    {!home&&<section className="surface"><h2>Seven-day overview</h2><div className="table-scroll" role="region" aria-label="Data table; scroll horizontally for all columns" tabIndex={0}><table><caption>Consumed nutrition in {data.timezone}; unknown means incomplete facts</caption><thead><tr><th>Local day</th><th>Meals</th>{nutrientFields.map(f=><th key={f}>{f.replace("_g","")} ({f==="calories"?"kcal":"g"})</th>)}</tr></thead><tbody>{data.days.map(d=><tr key={d.day}><th>{d.day}</th><td>{d.meal_count}</td>{nutrientFields.map(f=><td key={f}>{displayNutrient(d.nutrients[f].total)}</td>)}</tr>)}</tbody></table></div></section>}
    <section className="surface"><div className="surface-heading"><h2>Eaten meals</h2><Link className="button secondary compact" href="/meals">All meal history</Link></div>{data.meals.length?<MealRows meals={data.meals}/>:<p className="muted">No eaten meals recorded for this local day.</p>}</section>
    {home&&<section className="surface"><h2>Recipes and products</h2><p className="muted">The corrected catalog is awaiting validation. You can use provider food facts while adding a meal.</p><Link className="button secondary" href="/search">Catalog status</Link></section>}
    </>}
  </>;
}
