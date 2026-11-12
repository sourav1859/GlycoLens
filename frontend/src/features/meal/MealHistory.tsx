"use client";
import Link from "next/link";
import { useResource } from "../../lib/use-resource";
import { displayNutrient, isMeal, type Meal } from "../../lib/meal-facts";
import { PageIntro } from "../../components/layout/PageIntro";
import { AsyncState } from "../../components/ui/AsyncState";
import { useState } from "react";
import { isNutritionSummary } from "../../lib/nutrition";
import { displayNutrient as nutrientValue, nutrientFields } from "../../lib/meal-facts";
import { useAccount } from "../auth/AccountProvider";

function valid(value:unknown):value is {meals:Meal[];has_more:boolean} { const v=value as {meals?:unknown[];has_more?:boolean};return !!v&&Array.isArray(v.meals)&&v.meals.every(isMeal)&&typeof v.has_more==="boolean"; }
export function MealRows({meals}:{meals:Meal[]}) { const {account}=useAccount();const zone=account?.preferences.timezone??"UTC";return <div className="meal-list">{meals.map(m=><Link href={`/meals/${m.id}`} className="meal-row" key={m.id}><div><strong>{m.name}</strong><p className="small muted">{m.state} · {new Date(m.consumed_at??m.recorded_at).toLocaleString(undefined,{timeZone:zone})} ({zone}) · revision {m.revision}</p></div><span>{displayNutrient(m.calories)} kcal</span></Link>)}</div>; }
export function MealHistory() {
  const [offset,setOffset]=useState(0),[day,setDay]=useState(""),[slot,setSlot]=useState(""); const {data,error,reload}=useResource(`/meals?offset=${offset}${day?`&day=${day}`:""}${slot?`&slot=${slot}`:""}`,valid);
  const nutrition=useResource(`/nutrition${day?`?day=${day}`:""}`,isNutritionSummary);const daily=nutrition.data?.days.at(-1);
  return <><PageIntro eyebrow="Your reviewed meals" title="Meal log" description="Planned, eaten and cancelled meals in your selected source session."><Link className="button" href="/meals/new">Add a meal</Link></PageIntro>
    <section className="surface"><h2>Eaten totals {day||nutrition.data?.day||""}</h2>{nutrition.error?<AsyncState title="Daily totals unavailable" message={nutrition.error} error retry={nutrition.reload}/>:nutrition.data?.available?<dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{nutrientValue(daily?.nutrients[f].total)} {f==="calories"?"kcal":"g"}</dd></div>)}</dl>:<p className="muted">Prepare a source to see daily totals.</p>}</section>
    <section className="surface"><div className="form-grid"><label>Filter by local day<input type="date" value={day} onChange={e=>{setDay(e.target.value);setOffset(0);}}/></label><label>Meal slot<select value={slot} onChange={e=>{setSlot(e.target.value);setOffset(0);}}><option value="">All slots</option>{["breakfast","lunch","dinner","snack"].map(s=><option key={s} value={s}>{s}</option>)}</select></label></div><button className="button secondary compact" onClick={()=>{setDay("");setSlot("");setOffset(0);}}>Clear filters</button>{error?<AsyncState title="Meal history unavailable" message={error} error retry={reload}/>:!data?<AsyncState title="Loading meals…"/>:data.meals.length?<MealRows meals={data.meals}/>:<AsyncState title="No meals in this source session" message="Add a reviewed meal or prepare a virtual source from Home."/>}
    <div className="intro-actions"><button className="button secondary" disabled={!offset} onClick={()=>setOffset(Math.max(0,offset-20))}>Previous</button><button className="button secondary" disabled={!data?.has_more} onClick={()=>setOffset(offset+20)}>Next</button></div></section></>;
}
