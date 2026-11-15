"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { BrowserMultiFormatReader, IScannerControls } from "@zxing/browser";
import { api, enterDemo } from "../../lib/application-api";
import { expectedFacts, type Food as GroundedFood } from "../../lib/meal-facts";
import { ForecastChart } from "../../components/ForecastChart";
import { ForecastResponse, isForecastResponse } from "../../types/forecast";
import Link from "next/link";
import { useWorkspace } from "../simulation/Workspace";
import { useMealDrafts } from "./MealDrafts";
import { SourceAdvance } from "../forecast/SourceAdvance";
import { useAccount } from "../auth/AccountProvider";
import { ForecastModelPicker, type ModelKey } from "../forecast/ForecastModelPicker";

type Food = Omit<GroundedFood,"nutrient_basis_g"> & {nutrient_basis_g?:number};
type Item = { food: Food; grams: number };
type Ingredient = { name: string; quantity: number; unit: string; needs_review: boolean };
type Similar = { id: string; name: string; similarity: number; actual_60: number };
type Reading = { recorded_at: string; glucose_mg_dl: number; source: string };

export function MealWorkflow({initialSourceId}:{initialSourceId?:string}) {
  const { session,account } = useAccount();
  async function enter() { await enterDemo(); }
  return <Workflow key={`${session?.user.id??"guest"}:${initialSourceId??"current"}`} ready={!!session&&!!account} enter={enter} initialSourceId={initialSourceId}/>;
}

function Workflow({ready,enter,initialSourceId}:{ready:boolean;enter:()=>Promise<void>;initialSourceId?:string}) {
  const {source,select,generation}=useWorkspace(),{account}=useAccount(),drafts=useMealDrafts();
  const [sourceId,setSourceId]=useState(initialSourceId??source?.id??"");
  const draftKey=`${account?.user_id}:simulation:${sourceId||"new"}`;
  const [draft]=useState(()=>drafts.read(draftKey));
  const alive=useRef(true);
  useEffect(()=>{alive.current=true;return()=>{alive.current=false;};},[]);
  const hydrated = useSyncExternalStore(() => () => {}, () => true, () => false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [origin, setOrigin] = useState(draft?.at??source?.clock_at??"");
  const [modelKey,setModelKey]=useState<ModelKey>("chronos");
  const [protocol,setProtocol]=useState("m1_fixed_meal_day");
  const [sourceSamples,setSourceSamples]=useState(source?.sample_count??0);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [mode, setMode] = useState(draft?.mode??"search");
  const [query, setQuery] = useState(draft?.query??"synthetic");
  const [foods, setFoods] = useState<Food[]>(draft?.foods??[]);
  const [code, setCode] = useState(draft?.code??"");
  const [recipe, setRecipe] = useState(draft?.recipe??"");
  const [ingredients, setIngredients] = useState<Ingredient[]>(draft?.ingredients??[]);
  const [items, setItems] = useState<Item[]>(draft?.items??[]);
  const [servings, setServings] = useState(draft?.servings??1);
  const [name, setName] = useState(draft?.name??"My planned meal");
  const [confirmed, setConfirmed] = useState(false);
  const [mealId, setMealId] = useState(draft?.simulationMealId??"");
  const [forecast, setForecast] = useState<ForecastResponse>();
  const [similar, setSimilar] = useState<Similar[]>([]);
  const key = useRef<string>(draft?.requestKey??"");
  const forecastKey = useRef<string>("");
  const video = useRef<HTMLVideoElement>(null);
  const scanner = useRef<IScannerControls | undefined>(undefined);

  useEffect(()=>{
    if(!ready||!sourceId)return;
    let active=true;
    const requestGeneration=generation.current;
    void Promise.all([api(`/simulation/sources/${sourceId}`),api(`/timeline?source_session_id=${sourceId}`)]).then(([record,timeline])=>{
      if(!active||requestGeneration!==generation.current)return;
      setOrigin(record.clock_at);setReadings(timeline.cgm);setSourceSamples(timeline.cgm.length);
      setProtocol(timeline.cgm.length>=288?"lightgbm_warmup_48h_v1":"m1_fixed_meal_day");
      select({id:record.id,clock_at:record.clock_at,sample_count:timeline.cgm.length});
    }).catch(e=>{if(active)setError(e instanceof Error?e.message:"Simulation session unavailable");});
    return()=>{active=false;};
  },[ready,sourceId,select,generation]);
  useEffect(()=>{
    if(items.length||recipe||code||name!=="My planned meal"||query!=="synthetic")drafts.write(draftKey,{mode,query,code,recipe,items:items as {food:GroundedFood;grams:number}[],foods:foods as GroundedFood[],ingredients,name,servings,portion:1,at:origin,consumedAt:"",state:"planned",requestKey:key.current,mealType:"",simulationMealId:mealId});
  },[drafts,draftKey,mode,query,code,recipe,items,foods,ingredients,name,servings,origin,mealId]);
  useEffect(()=>{
    if(mealId||!(items.length||recipe||code||name!=="My planned meal"))return;
    const warn=(event:BeforeUnloadEvent)=>{event.preventDefault();event.returnValue="";};
    window.addEventListener("beforeunload",warn);return()=>window.removeEventListener("beforeunload",warn);
  },[mealId,items.length,recipe,code,name]);
  async function refreshSource(){
    if(!sourceId)return;
    const requestGeneration=generation.current;
    const record=await api(`/simulation/sources/${sourceId}`);
    const timeline=await api(`/timeline?source_session_id=${sourceId}`);
    if(!alive.current||requestGeneration!==generation.current)return;
    setOrigin(record.clock_at);setReadings(timeline.cgm);select({id:sourceId,clock_at:record.clock_at,sample_count:timeline.cgm.length});changed();
  }
  useEffect(() => () => scanner.current?.stop(), []);
  useEffect(() => { scanner.current?.stop(); }, [mode]);

  async function action(label: string, work: () => Promise<void>) {
    setBusy(label); setError("");
    try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Request failed"); }
    finally { setBusy(""); }
  }
  function changed() { setConfirmed(false); setMealId(""); setForecast(undefined); setSimilar([]); key.current = ""; forecastKey.current = ""; }
  function editIngredient(index: number, update: Partial<Ingredient>) {
    setIngredients(ingredients.map((value, i) => i === index ? { ...value, ...update, needs_review: true } : value));
    changed();
  }
  async function runSimulation(replay = false, selectedProtocol=protocol) {
    const requestGeneration=generation.current;
    const result = await api("/simulation/scenario", { method: "POST", body: JSON.stringify({ replay,protocol:selectedProtocol }) });
    if(!alive.current||requestGeneration!==generation.current)return;
    setProtocol(selectedProtocol);setSourceSamples(result.sample_count??0);
    setOrigin(result.forecast_origin);setSourceId(result.source_session_id);
    select({id:result.source_session_id,clock_at:result.forecast_origin,sample_count:result.sample_count});
    setNotice(`${result.execution === "live" ? "New simulation completed" : "Saved simulation replayed"}. ${result.notice}`);
    const timeline=await api(`/timeline?source_session_id=${result.source_session_id}`);
    if(alive.current){setReadings(timeline.cgm);changed();}
  }
  async function lookupBarcode(barcode: string) { const food = await api(`/foods/barcode/${encodeURIComponent(barcode)}`); setFoods([food]); }
  async function scan() {
    if (!video.current) return;
    scanner.current?.stop();
    const reader = new BrowserMultiFormatReader();
    scanner.current = await reader.decodeFromVideoDevice(undefined, video.current, (result, _error, controls) => {
      if (result) { controls.stop(); setCode(result.getText()); void action("Looking up barcode", () => lookupBarcode(result.getText())); }
    });
  }
  const fields = ["calories", "carbs_g", "protein_g", "fat_g", "fiber_g"] as const;
  const totals = Object.fromEntries(fields.map(field => [field, items.length && items.every(item=>typeof item.food[field]==="number" && Number.isFinite(item.food[field])) ? items.reduce((sum, item) => sum + Number(item.food[field] ?? 0) * item.grams / Number(item.food.nutrient_basis_g ?? 100) / servings, 0) : null]));
  const complete = items.length > 0 && servings > 0 && Number.isFinite(servings) && items.every(item => item.food.id && item.grams > 0 && Number.isFinite(item.grams) && fields.every(field => typeof item.food[field] === "number"));

  return <section className="meal-workflow" aria-labelledby="workflow-title">
    <h2 id="workflow-title">Plan a meal with a virtual patient</h2>
    <p>Research and education only. Forecasts are uncertain estimates and must not guide insulin dosing or treatment.</p>
    {error && <p role="alert" className="error-message">{error}</p>}
    <p role="status" aria-live="polite">{busy || notice}</p>
    {!ready ? <button disabled={!hydrated || !!busy} onClick={() => void action("Entering demo", enter)}>Choose virtual patient</button> : <>
      <section className="workflow-panel">
        <h3>Glucose context</h3>
        <p>Source: py-mgipsim virtual patient. Virtual clock: {origin ? new Date(origin).toLocaleString(undefined,{timeZone:account?.preferences.timezone??"UTC"}) : "Run the scenario to begin"}</p>
        {sourceId&&<><p className="small">Session {sourceId.slice(0,8)} · {account?.preferences.timezone??"UTC"}. <Link href="/demo/meals">All simulation meal history</Link></p><SourceAdvance source={{id:sourceId,clock_at:origin}} onAdvanced={()=>void action("Refreshing virtual clock",refreshSource)}/></>}
        <label className="field">Simulation protocol<select value={protocol} disabled={!!busy} onChange={e=>setProtocol(e.target.value)}><option value="m1_fixed_meal_day">Original one-day demo</option><option value="lightgbm_warmup_48h_v1">48-hour research warm-up</option></select></label>
        <button disabled={!!busy} onClick={() => void action("Running new simulation", () => runSimulation())}>Run new simulation</button>{" "}
        <button disabled={!!busy} onClick={() => void action("Replaying saved simulation", () => runSimulation(true))}>Replay saved simulation</button>
        <p className="small">Both use the selected fixed virtual-patient protocol and its simulation clock. Replay needs that protocol saved on this server. The 48-hour protocol provides history for LightGBM; user meal edits do not change either simulator&apos;s preset meals.</p>
        <ForecastModelPicker value={modelKey} onChange={value=>{setModelKey(value);forecastKey.current="";setForecast(undefined);setSimilar([]);}} disabled={!!busy} ready={ready} prepareLong={()=>void action("Preparing 48-hour research source",()=>runSimulation(false,"lightgbm_warmup_48h_v1"))}/>
        {readings.length > 0 && <><p>Latest simulated glucose: {Number(readings[0].glucose_mg_dl).toFixed(0)} mg/dL</p>
          <svg viewBox="0 0 600 140" role="img" aria-label="Recent simulated glucose timeline"><polyline fill="none" stroke="#176b5d" strokeWidth="3" points={[...readings.slice(0, 24)].reverse().map((p, i) => `${i * 25},${130 - Math.max(0, Math.min(120, (Number(p.glucose_mg_dl) - 20) / 4))}`).join(" ")} /></svg></>}
      </section>
      <section className="workflow-panel">
        <h3>Add your meal</h3>
        <div className="meal-tabs" role="group" aria-label="Meal input method">{["search", "barcode", "recipe"].map(value => <button key={value} aria-pressed={mode === value} onClick={() => setMode(value)}>{value === "search" ? "Food search" : value === "barcode" ? "Barcode" : "Recipe text"}</button>)}</div>
        {mode === "recipe" && <><label>Home recipe<textarea value={recipe} onChange={e => setRecipe(e.target.value)} maxLength={4000} placeholder="200 g rice, 100 g chicken; two servings" /></label>
          <button disabled={!!busy || recipe.length < 3} onClick={() => void action("Extracting ingredients", async () => { const result = await api("/meals/parse-recipe", { method: "POST", body: JSON.stringify({ text: recipe }) }); setIngredients(result.ingredients); setServings(result.servings); changed(); })}>Extract ingredients</button>
          <p>Confirm each ingredient and measure its grams before adding it. Nutrients come from food databases.</p>
          {ingredients.map((ingredient, index) => <div key={index} className="ingredient-row"><input aria-label={`Ingredient ${index + 1}`} value={ingredient.name} onChange={e => editIngredient(index, { name: e.target.value })} /><input type="number" min="0.01" step="any" aria-label={`Ingredient ${index + 1} quantity`} value={ingredient.quantity} onChange={e => editIngredient(index, { quantity: Number(e.target.value) })} /><input aria-label={`Ingredient ${index + 1} unit`} value={ingredient.unit} onChange={e => editIngredient(index, { unit: e.target.value })} /><button onClick={() => { setQuery(ingredient.name); setMode("search"); }}>Find food facts</button><span>{ingredient.needs_review ? "Review required" : "Confirm quantity"}</span></div>)}</>}
        {mode === "barcode" && <><label>Barcode number<input value={code} onChange={e => setCode(e.target.value)} inputMode="numeric" /></label><button disabled={!!busy} onClick={() => void action("Looking up barcode", () => lookupBarcode(code))}>Look up barcode</button>{" "}<button disabled={!!busy} onClick={() => void action("Starting camera", scan)}>Scan with camera</button><video ref={video} muted playsInline aria-label="Barcode camera preview" /><button onClick={() => scanner.current?.stop()}>Stop camera</button></>}
        {mode === "search" && <><label>Search food<input value={query} onChange={e => setQuery(e.target.value)} /></label><button disabled={!!busy || query.length < 2} onClick={() => void action("Searching foods", async () => { const result = await api(`/foods/search?q=${encodeURIComponent(query)}`); setFoods([...(result.foods ?? []), ...(result.candidates ?? [])]); setNotice(result.notice ?? "Choose a matching food and review its source"); })}>Search foods</button></>}
        {foods.map(food => <div key={`${food.source}:${food.source_food_id}`} className="food-result"><span>{food.name} · {food.source}</span><button disabled={!!busy} onClick={() => void action("Loading food facts", async () => { const resolved: Food = food.id ? food : await api(`/foods/usda/${food.source_food_id}`); setItems([...items, { food: resolved, grams: 100 }]); changed(); })}>Add ingredient</button></div>)}
      </section>
      <section className="workflow-panel">
        <h3>Nutrition review</h3>
        <label>Meal name<input value={name} onChange={e => { setName(e.target.value); changed(); }} maxLength={200} /></label>
        <label>Recipe servings<input type="number" min="1" step="any" value={servings} onChange={e => { setServings(Number(e.target.value)); changed(); }} /></label>
        {items.map((item, index) => <div className="ingredient-row" key={index}><span>{item.food.name} · {item.food.source}</span><label>Ingredient grams<input type="number" min="0.01" max="10000" step="any" value={item.grams} onChange={e => { setItems(items.map((v, i) => i === index ? { ...v, grams: Number(e.target.value) } : v)); changed(); }} /></label><button onClick={() => { setItems(items.filter((_, i) => i !== index)); changed(); }}>Remove</button></div>)}
        <dl className="nutrition-totals">{fields.map(field => <div key={field}><dt>{field.replace("_g", "").replace("carbs", "Carbohydrates")}</dt><dd>{totals[field]===null ? "Unknown" : Number(totals[field]).toFixed(1)} {field === "calories" ? "kcal" : "g"}</dd></div>)}</dl>
        {!complete && <p>Choose food facts with all nutrients available and verify ingredient amounts.</p>}
        <label className="confirmation"><input type="checkbox" checked={confirmed} disabled={!complete} onChange={e => setConfirmed(e.target.checked)} />I reviewed the food matches, grams, servings and nutrition sources.</label>
        <button disabled={!!busy || !confirmed || !origin} onClick={() => void action("Saving confirmed meal", async () => { if (!key.current) key.current = crypto.randomUUID(); const result = await api("/meals", { method: "POST", body: JSON.stringify({ workspace:"simulation", source_session_id:sourceId, name, recorded_at: origin, idempotency_key: key.current, items: items.map(item => ({ food_id: item.food.id, grams: item.grams / servings, expected_facts: expectedFacts({...item.food,nutrient_basis_g:item.food.nutrient_basis_g??100} as GroundedFood) })), input_snapshot: { entry_method: mode, servings, confirmed: true } }) }); setMealId(result.meal_id); setNotice("Meal saved. Stored in simulation history, separate from personal meals. Ready to run the selected forecast model."); })}>Save meal</button>{" "}
        <button disabled={!!busy || !mealId || (modelKey === "lightgbm" && sourceSamples < 288)} onClick={() => void action("Running selected forecast model", async () => { if (!forecastKey.current) forecastKey.current = crypto.randomUUID(); const result = await api("/forecasts", { method: "POST", body: JSON.stringify({ meal_id: mealId, idempotency_key: forecastKey.current, model_key:modelKey }) }); const data = result.forecast ?? (await api(`/forecasts/${result.forecast_id}`)).forecast; if (!isForecastResponse(data)) throw new Error("Forecast response failed validation"); setForecast(data); const history = await api(`/meals/${mealId}/similar`); setSimilar(history.meals); })}>Run forecast</button>
        {mealId&&<p><Link href={`/demo/meals/${mealId}`}>Open saved simulation meal</Link></p>}
        {modelKey==="lightgbm"&&sourceSamples<288&&<p className="small">Start the 48-hour research simulation, then review and save your meal before running LightGBM.</p>}
      </section>
      {forecast && <ForecastChart data={forecast} />}
      {forecast && <section className="workflow-panel"><h3>Similar earlier meals</h3><p>Same-session simulated history, ranked by nutrient distance. Earlier nutrition is illustrative; glucose outcomes come from the simulator.</p>{similar.length ? similar.map(meal => <p key={meal.id}>{meal.name} · similarity {meal.similarity.toFixed(2)} · actual +60 min {Number(meal.actual_60).toFixed(0)} mg/dL</p>) : <p>No completed earlier meals match this context.</p>}</section>}
    </>}
  </section>;
}
