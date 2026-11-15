"use client";
import { useResource } from "../../lib/use-resource";
import { isNutritionSummary } from "../../lib/nutrition";
import { displayNutrient,nutrientFields } from "../../lib/meal-facts";
import { MealRows } from "../meal/MealHistory";
import { AsyncState } from "../../components/ui/AsyncState";

export function SimulationNutrition({sourceId}:{sourceId:string}) {
  const {data,error,reload}=useResource(`/nutrition?workspace=simulation&source_session_id=${encodeURIComponent(sourceId)}`,isNutritionSummary);
  if(error)return <AsyncState title="Virtual daily totals unavailable" message={error} error retry={reload}/>;
  if(!data)return <AsyncState title="Loading virtual day…"/>;
  const day=data.days.at(-1);
  return <section className="surface"><h2>Simulation eaten totals · {data.day}</h2><p className="small muted">Session {sourceId.slice(0,8)} · {data.timezone}. Only explicitly eaten meals in this virtual day; never personal consumption.</p><dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{displayNutrient(day?.nutrients[f].total)} {f==="calories"?"kcal":"g"}</dd></div>)}</dl>{data.meals.length?<MealRows meals={data.meals}/>:<p>No eaten virtual meals in this session/day. Saved planned meals remain in Simulation meals.</p>}</section>;
}
