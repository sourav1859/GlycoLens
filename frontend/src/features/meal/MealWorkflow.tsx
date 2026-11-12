"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { BrowserMultiFormatReader, IScannerControls } from "@zxing/browser";
import { api, enterDemo } from "../../lib/application-api";
import { expectedFacts, type Food as GroundedFood } from "../../lib/meal-facts";
import { ForecastChart } from "../../components/ForecastChart";
import { ForecastResponse, isForecastResponse } from "../../types/forecast";
import { useAccount } from "../auth/AccountProvider";

type Food = { id?: string; name: string; source: string; source_food_id: string; nutrient_basis_g?: number; calories?: number; carbs_g?: number; protein_g?: number; fat_g?: number; fiber_g?: number };
type Item = { food: Food; grams: number };
type Ingredient = { name: string; quantity: number; unit: string; needs_review: boolean };
type Similar = { id: string; name: string; similarity: number; actual_60: number };
type Reading = { recorded_at: string; glucose_mg_dl: number; source: string };

export function MealWorkflow() {
  const { session } = useAccount();
  const [enteredUser, setEnteredUser] = useState("");
  async function enter() { const result = await enterDemo(); setEnteredUser(result.user_id); }
  return <Workflow key={session?.user.id ?? "guest"} ready={!!session && enteredUser === session.user.id} enter={enter} />;
}

function Workflow({ ready, enter }: { ready: boolean; enter: () => Promise<void> }) {
  const hydrated = useSyncExternalStore(() => () => {}, () => true, () => false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [origin, setOrigin] = useState("");
  const [readings, setReadings] = useState<Reading[]>([]);
  const [mode, setMode] = useState("search");
  const [query, setQuery] = useState("synthetic");
  const [foods, setFoods] = useState<Food[]>([]);
  const [code, setCode] = useState("");
  const [recipe, setRecipe] = useState("");
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [servings, setServings] = useState(1);
  const [name, setName] = useState("My planned meal");
  const [confirmed, setConfirmed] = useState(false);
  const [mealId, setMealId] = useState("");
  const [forecast, setForecast] = useState<ForecastResponse>();
  const [similar, setSimilar] = useState<Similar[]>([]);
  const key = useRef<string>("");
  const forecastKey = useRef<string>("");
  const video = useRef<HTMLVideoElement>(null);
  const scanner = useRef<IScannerControls | undefined>(undefined);

  useEffect(() => () => scanner.current?.stop(), []);
  useEffect(() => { scanner.current?.stop(); }, [mode]);

  async function action(label: string, work: () => Promise<void>) {
    setBusy(label); setError("");
    try { await work(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Request failed"); }
    finally { setBusy(""); }
  }
  function changed() { setConfirmed(false); setMealId(""); setForecast(undefined); setSimilar([]); key.current = ""; forecastKey.current = ""; }
  async function runSimulation(replay = false) {
    const result = await api("/simulation/scenario", { method: "POST", body: JSON.stringify({ replay }) });
    setOrigin(result.forecast_origin);
    setNotice(`${result.execution === "live" ? "New simulation completed" : "Saved simulation replayed"}. ${result.notice}`);
    const timeline = await api("/timeline"); setReadings(timeline.cgm); changed();
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
  const totals = Object.fromEntries(fields.map(field => [field, items.reduce((sum, item) => sum + Number(item.food[field] ?? 0) * item.grams / Number(item.food.nutrient_basis_g ?? 100) / servings, 0)]));
  const complete = items.length > 0 && servings > 0 && Number.isFinite(servings) && items.every(item => item.food.id && item.grams > 0 && Number.isFinite(item.grams) && fields.every(field => typeof item.food[field] === "number"));

  return <section className="meal-workflow" aria-labelledby="workflow-title">
    <h2 id="workflow-title">Plan a meal with a virtual patient</h2>
    <p>Research and education only. Forecasts are uncertain estimates and must not guide insulin dosing or treatment.</p>
    {error && <p role="alert" className="error-message">{error}</p>}
    <p role="status" aria-live="polite">{busy || notice}</p>
    {!ready ? <button disabled={!hydrated || !!busy} onClick={() => void action("Entering demo", enter)}>Choose virtual patient</button> : <>
      <section className="workflow-panel">
        <h3>Glucose context</h3>
        <p>Source: py-mgipsim virtual patient. Clock: {origin ? new Date(origin).toUTCString() : "Run the scenario to begin"}</p>
        <button disabled={!!busy} onClick={() => void action("Running new simulation", () => runSimulation())}>Run new simulation</button>{" "}
        <button disabled={!!busy} onClick={() => void action("Replaying saved simulation", () => runSimulation(true))}>Replay saved simulation</button>
        <p className="small">Both use the fixed virtual-patient scenario and its simulation clock. Replay needs a simulation saved on this server.</p>
        {readings.length > 0 && <><p>Latest simulated glucose: {Number(readings[0].glucose_mg_dl).toFixed(0)} mg/dL</p>
          <svg viewBox="0 0 600 140" role="img" aria-label="Recent simulated glucose timeline"><polyline fill="none" stroke="#176b5d" strokeWidth="3" points={[...readings.slice(0, 24)].reverse().map((p, i) => `${i * 25},${130 - Math.max(0, Math.min(120, (Number(p.glucose_mg_dl) - 20) / 4))}`).join(" ")} /></svg></>}
      </section>
      <section className="workflow-panel">
        <h3>Add your meal</h3>
        <div className="meal-tabs" role="group" aria-label="Meal input method">{["search", "barcode", "recipe"].map(value => <button key={value} aria-pressed={mode === value} onClick={() => setMode(value)}>{value === "search" ? "Food search" : value === "barcode" ? "Barcode" : "Recipe text"}</button>)}</div>
        {mode === "recipe" && <><label>Home recipe<textarea value={recipe} onChange={e => setRecipe(e.target.value)} maxLength={4000} placeholder="200 g rice, 100 g chicken; two servings" /></label>
          <button disabled={!!busy || recipe.length < 3} onClick={() => void action("Extracting ingredients", async () => { const result = await api("/meals/parse-recipe", { method: "POST", body: JSON.stringify({ text: recipe }) }); setIngredients(result.ingredients); setServings(result.servings); changed(); })}>Extract ingredients</button>
          <p>Confirm each ingredient and measure its grams before adding it. Nutrients come from food databases.</p>
          {ingredients.map((ingredient, index) => <div key={index} className="ingredient-row"><input aria-label={`Ingredient ${index + 1}`} value={ingredient.name} onChange={e => setIngredients(ingredients.map((v, i) => i === index ? { ...v, name: e.target.value } : v))} /><input type="number" min="0.01" step="any" aria-label={`Ingredient ${index + 1} quantity`} value={ingredient.quantity} onChange={e => setIngredients(ingredients.map((v, i) => i === index ? { ...v, quantity: Number(e.target.value) } : v))} /><input aria-label={`Ingredient ${index + 1} unit`} value={ingredient.unit} onChange={e => setIngredients(ingredients.map((v, i) => i === index ? { ...v, unit: e.target.value } : v))} /><button onClick={() => { setQuery(ingredient.name); setMode("search"); }}>Find food facts</button><span>{ingredient.needs_review ? "Review required" : "Confirm quantity"}</span></div>)}</>}
        {mode === "barcode" && <><label>Barcode number<input value={code} onChange={e => setCode(e.target.value)} inputMode="numeric" /></label><button disabled={!!busy} onClick={() => void action("Looking up barcode", () => lookupBarcode(code))}>Look up barcode</button>{" "}<button disabled={!!busy} onClick={() => void action("Starting camera", scan)}>Scan with camera</button><video ref={video} muted playsInline aria-label="Barcode camera preview" /><button onClick={() => scanner.current?.stop()}>Stop camera</button></>}
        {mode === "search" && <><label>Search food<input value={query} onChange={e => setQuery(e.target.value)} /></label><button disabled={!!busy || query.length < 2} onClick={() => void action("Searching foods", async () => { const result = await api(`/foods/search?q=${encodeURIComponent(query)}`); setFoods([...(result.foods ?? []), ...(result.candidates ?? [])]); setNotice(result.notice ?? "Choose a matching food and review its source"); })}>Search foods</button></>}
        {foods.map(food => <div key={`${food.source}:${food.source_food_id}`} className="food-result"><span>{food.name} · {food.source}</span><button disabled={!!busy} onClick={() => void action("Loading food facts", async () => { const resolved: Food = food.id ? food : await api(`/foods/usda/${food.source_food_id}`); setItems([...items, { food: resolved, grams: 100 }]); changed(); })}>Add ingredient</button></div>)}
      </section>
      <section className="workflow-panel">
        <h3>Nutrition review</h3>
        <label>Meal name<input value={name} onChange={e => { setName(e.target.value); changed(); }} maxLength={200} /></label>
        <label>Recipe servings<input type="number" min="1" step="any" value={servings} onChange={e => { setServings(Number(e.target.value)); changed(); }} /></label>
        {items.map((item, index) => <div className="ingredient-row" key={index}><span>{item.food.name} · {item.food.source}</span><label>Ingredient grams<input type="number" min="0.01" max="10000" step="any" value={item.grams} onChange={e => { setItems(items.map((v, i) => i === index ? { ...v, grams: Number(e.target.value) } : v)); changed(); }} /></label><button onClick={() => { setItems(items.filter((_, i) => i !== index)); changed(); }}>Remove</button></div>)}
        <dl className="nutrition-totals">{fields.map(field => <div key={field}><dt>{field.replace("_g", "").replace("carbs", "Carbohydrates")}</dt><dd>{Number(totals[field]).toFixed(1)} {field === "calories" ? "kcal" : "g"}</dd></div>)}</dl>
        {!complete && <p>Choose food facts with all nutrients available and verify ingredient amounts.</p>}
        <label className="confirmation"><input type="checkbox" checked={confirmed} disabled={!complete} onChange={e => setConfirmed(e.target.checked)} />I reviewed the food matches, grams, servings and nutrition sources.</label>
        <button disabled={!!busy || !confirmed || !origin} onClick={() => void action("Saving confirmed meal", async () => { if (!key.current) key.current = crypto.randomUUID(); const result = await api("/meals", { method: "POST", body: JSON.stringify({ name, recorded_at: origin, idempotency_key: key.current, items: items.map(item => ({ food_id: item.food.id, grams: item.grams / servings, expected_facts: expectedFacts({...item.food,nutrient_basis_g:item.food.nutrient_basis_g??100} as GroundedFood) })), input_snapshot: { entry_method: mode, servings, confirmed: true } }) }); setMealId(result.meal_id); setNotice("Meal saved. Ready to run the selected pretrained model."); })}>Save meal</button>{" "}
        <button disabled={!!busy || !mealId} onClick={() => void action("Running selected pretrained model", async () => { if (!forecastKey.current) forecastKey.current = crypto.randomUUID(); const result = await api("/forecasts", { method: "POST", body: JSON.stringify({ meal_id: mealId, idempotency_key: forecastKey.current }) }); const data = result.forecast ?? (await api(`/forecasts/${result.forecast_id}`)).forecast; if (!isForecastResponse(data)) throw new Error("Forecast response failed validation"); setForecast(data); const history = await api(`/meals/${mealId}/similar`); setSimilar(history.meals); })}>Run forecast</button>
      </section>
      {forecast && <ForecastChart data={forecast} />}
      {forecast && <section className="workflow-panel"><h3>Similar earlier meals</h3><p>Same-session simulated history, ranked by nutrient distance. Earlier nutrition is illustrative; glucose outcomes come from the simulator.</p>{similar.length ? similar.map(meal => <p key={meal.id}>{meal.name} · similarity {meal.similarity.toFixed(2)} · actual +60 min {Number(meal.actual_60).toFixed(0)} mg/dL</p>) : <p>No completed earlier meals match this context.</p>}</section>}
    </>}
  </section>;
}
