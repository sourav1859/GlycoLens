"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { BrowserMultiFormatReader, type IScannerControls } from "@zxing/browser";
import { api } from "../../lib/application-api";
import { displayNutrient, expectedFacts, isFood, isMeal, nutrientFields, portionFacts, type DraftItem, type Food, type Meal } from "../../lib/meal-facts";
import { useAccount } from "../auth/AccountProvider";
import { PageIntro } from "../../components/layout/PageIntro";
import { AsyncState } from "../../components/ui/AsyncState";

import { useMealDrafts } from "./MealDrafts";

type Ingredient = { name:string; quantity:number; unit:string; needs_review:boolean };
export function MealComposer({ initialMode="search", mealId, copyId }: { initialMode?:string; mealId?:string; copyId?:string }) {
  const { account } = useAccount(), router=useRouter();
  const drafts=useMealDrafts(),draftKey=mealId?`edit:${mealId}`:copyId?`copy:${copyId}`:"new";
  const [initialDraft]=useState(()=>drafts.read(draftKey));
  const [mode,setMode]=useState(initialDraft?.mode??initialMode), [query,setQuery]=useState(initialDraft?.query??""), [code,setCode]=useState(initialDraft?.code??""), [recipe,setRecipe]=useState(initialDraft?.recipe??"");
  const [items,setItems]=useState<DraftItem[]>(initialDraft?.items??[]), [foods,setFoods]=useState<Food[]>(initialDraft?.foods??[]), [ingredients,setIngredients]=useState<Ingredient[]>(initialDraft?.ingredients??[]);
  const [name,setName]=useState(initialDraft?.name??"My meal"), [servings,setServings]=useState(initialDraft?.servings??1), [portion,setPortion]=useState(initialDraft?.portion??1), [at,setAt]=useState(initialDraft?.at??""),[consumedAt,setConsumedAt]=useState(initialDraft?.consumedAt??"");
  const [state,setState]=useState<"planned"|"logged">(initialDraft?.state??"planned"), [meal,setMeal]=useState<Meal|undefined>(initialDraft?.meal), [confirmed,setConfirmed]=useState(false);
  const [busy,setBusy]=useState(""), [error,setError]=useState(""), [notice,setNotice]=useState("");
  const [mealType,setMealType]=useState(initialDraft?.mealType??"");
  const requestKey=useRef(initialDraft?.requestKey??""), video=useRef<HTMLVideoElement>(null), scanner=useRef<IScannerControls | undefined>(undefined);
  useEffect(() => () => scanner.current?.stop(), []);
  useEffect(() => { scanner.current?.stop(); }, [mode]);
  useEffect(() => {
    if(initialDraft)return;
    let active=true;
    void api(mealId || copyId ? `/meals/${mealId || copyId}` : "/nutrition").then(value => {
      if (!active) return;
      if (mealId || copyId) {
        if (!Array.isArray(value) || !isMeal(value[0])) throw new Error("Meal unavailable");
        const original=value[0]; setMeal(mealId ? original : undefined); setName(copyId ? `Copy of ${original.name}`.slice(0,200) : original.name);
        const copied=copyId?original.meal_items?.map(row=>({food:row.foods,grams:row.grams})):original.nutrition_provenance.food_snapshots.map(f=>({food:{...f,id:f.food_id},grams:f.grams}));if(!copied?.every(i=>isFood(i.food)&&i.food.id))throw new Error("Current food facts are unavailable; review the foods again");setItems(copied);
        setMealType(original.meal_type??"");setAt(original.recorded_at); setConsumedAt(original.consumed_at??original.recorded_at); setState(mealId && original.state==="logged" ? "logged" : "planned");
      } else if (value.source?.clock_at) setAt(value.source.clock_at);
    }).catch(reason=>{if(active)setError(reason instanceof Error?reason.message:"Meal unavailable");});
    return ()=>{active=false;};
  }, [mealId,copyId,initialDraft]);
  useEffect(()=>{if(items.length||recipe||query||code||name!=="My meal")drafts.write(draftKey,{mode,query,code,recipe,items,foods,ingredients,name,servings,portion,at,consumedAt,state,meal,requestKey:requestKey.current,mealType});},[drafts,draftKey,mode,query,code,recipe,items,foods,ingredients,name,servings,portion,at,consumedAt,state,meal,mealType]);
  useEffect(()=>{if(!items.length)return;const warn=(event:BeforeUnloadEvent)=>{event.preventDefault();event.returnValue="";};window.addEventListener("beforeunload",warn);return()=>window.removeEventListener("beforeunload",warn);},[items.length]);
  function changed() { setConfirmed(false); requestKey.current=""; }
  async function action(label:string, work:()=>Promise<void>) {
    setBusy(label); setError(""); try { await work(); } catch(reason) { setError(reason instanceof Error?reason.message:"Request failed"); } finally { setBusy(""); }
  }
  async function barcode(value:string) {
    if (!/^\d{8,14}$/.test(value)) throw new Error("Enter an 8–14 digit product barcode");
    const food=await api(`/foods/barcode/${value}`); if(!isFood(food))throw new Error("Product facts failed validation"); setFoods([food]);
  }
  async function scan() {
    if(!video.current || !navigator.mediaDevices?.getUserMedia) throw new Error("Camera unavailable. Enter the barcode number instead.");
    scanner.current?.stop();
    scanner.current=await new BrowserMultiFormatReader().decodeFromVideoDevice(undefined,video.current,(result,_error,controls)=>{
      if(result) {controls.stop();setCode(result.getText());void action("Looking up product",()=>barcode(result.getText()));}
    });
  }
  const totals=portionFacts(items,servings,portion);
  const valid=items.length>0 && items.every(i=>i.food.id && i.grams/servings*portion<=10000) && totals && Number.isFinite(Date.parse(at)) && /(?:Z|[+-]\d\d:\d\d)$/.test(at);
  if(meal?.state==="cancelled")return <AsyncState title="This meal was cancelled" message="Use Copy as new draft on the meal detail page."/>;
  return <><PageIntro eyebrow="Review before saving" title={mealId?"Edit meal":"Add a meal"} description="Search provider food facts, scan a product, or review recipe ingredients. Saved totals are calculated by the server."/>
    {error&&<p role="alert" className="error-message">{error}</p>}<p role="status">{busy||notice}</p>
    <div className="dashboard-grid"><section className="surface"><h2>Find food facts</h2><p className="muted small">USDA and Open Food Facts are provider lookups. Our corrected recipe/product catalog is pending.</p>
      <div className="intro-actions" role="group" aria-label="Entry method">{["search","barcode","recipe"].map(m=><button className="button secondary compact" key={m} aria-pressed={mode===m} onClick={()=>setMode(m)}>{m==="search"?"Food search":m==="barcode"?"Product scan":"Recipe draft"}</button>)}</div>
      {mode==="search"&&<form onSubmit={e=>{e.preventDefault();void action("Searching",async()=>{const found=await api(`/foods/search?q=${encodeURIComponent(query)}`);const values=[...(found.foods??[]),...(found.candidates??[])];if(!values.every(isFood))throw new Error("Food results failed validation");setFoods(values);setNotice(found.notice??`${values.length} food matches`);});}}><label>Food name<input required minLength={2} maxLength={100} value={query} onChange={e=>setQuery(e.target.value)}/></label><button className="button" disabled={!!busy}>Search foods</button></form>}
      {mode==="barcode"&&<><label>Barcode number<input inputMode="numeric" value={code} onChange={e=>setCode(e.target.value)}/></label><div className="intro-actions"><button className="button" disabled={!!busy} onClick={()=>void action("Looking up product",()=>barcode(code))}>Look up product</button><button className="button secondary" disabled={!!busy} onClick={()=>void action("Starting camera",scan)}>Start camera</button><button className="button secondary" onClick={()=>scanner.current?.stop()}>Stop camera</button></div><video ref={video} muted playsInline className="scanner-preview" aria-label="Barcode preview"/><p className="small muted">If camera access is denied, enter the barcode manually. Check the product label and serving basis.</p></>}
      {mode==="recipe"&&<><label>Recipe text<textarea maxLength={4000} value={recipe} onChange={e=>setRecipe(e.target.value)} placeholder="Enter ingredients and recipe yield; do not include health or patient details"/></label><button className="button" disabled={!!busy||recipe.trim().length<3} onClick={()=>void action("Extracting ingredient draft",async()=>{const result=await api("/meals/parse-recipe",{method:"POST",body:JSON.stringify({text:recipe})});setIngredients(result.ingredients);setServings(result.servings);changed();})}>Extract draft</button><p className="small muted">Extraction produces an editable draft. Match every ingredient to food facts and measure grams; cups and pieces are not silently converted.</p>{ingredients.map((ingredient,index)=><div className="ingredient-row" key={index}><label>Ingredient {index+1}<input value={ingredient.name} onChange={e=>setIngredients(ingredients.map((v,i)=>i===index?{...v,name:e.target.value}:v))}/></label><span>{ingredient.quantity} {ingredient.unit} · review required</span><button className="button secondary compact" onClick={()=>{setQuery(ingredient.name);setMode("search");}}>Find food facts</button></div>)}</>}
      {foods.map((food,index)=><article className="food-result" key={`${food.source}:${food.source_food_id}:${index}`}><div><strong>{food.name}</strong><p className="small muted">{food.source} · facts per {food.nutrient_basis_g??100} g</p></div><button className="button secondary compact" disabled={!!busy} onClick={()=>void action("Loading food facts",async()=>{const resolved=food.id?food:await api(`/foods/usda/${encodeURIComponent(food.source_food_id)}`);if(!isFood(resolved)||!resolved.id)throw new Error("Food requires verified facts");setItems([...items,{food:resolved,grams:100}]);changed();})}>Add food</button></article>)}
    </section><section className="surface"><h2>Meal review</h2>{!mealId&&items.length>0&&<button className="button secondary compact" disabled={!!busy} onClick={()=>void action("Refreshing food facts",async()=>{const result=await api("/foods/cached",{method:"POST",body:JSON.stringify({ids:items.map(i=>i.food.id)})});if(!Array.isArray(result.foods)||!result.foods.every(isFood))throw new Error("Updated facts failed validation");const byId=new Map<string,Food>(result.foods.map((f:Food)=>[f.id!,f]));if(items.some(i=>!byId.has(i.food.id!)))throw new Error("Some food facts are unavailable");setItems(items.map(i=>({...i,food:byId.get(i.food.id!)!})));changed();})}>Refresh food facts for review</button>}<label>Meal name<input maxLength={200} value={name} onChange={e=>{setName(e.target.value);changed();}}/></label>
      <div className="form-grid"><label>Recipe yield in servings<input type="number" min="0.01" max="1000" step="any" value={servings} onChange={e=>{setServings(Number(e.target.value));changed();}}/></label><label>Servings in this meal<input type="number" min="0.01" max="1000" step="any" value={portion} onChange={e=>{setPortion(Number(e.target.value));changed();}}/></label></div>
      {items.map((item,index)=><div className="ingredient-row" key={index}><div><strong>{item.food.name}</strong><p className="small muted">{item.food.source}</p></div><label>Ingredient grams in recipe<input type="number" min="0.001" max="10000" step="any" value={item.grams} onChange={e=>{setItems(items.map((v,i)=>i===index?{...v,grams:Number(e.target.value)}:v));changed();}}/></label><button className="button secondary compact" onClick={()=>{setItems(items.filter((_,i)=>i!==index));changed();}}>Remove</button></div>)}
      <dl className="nutrition-totals">{nutrientFields.map(f=><div key={f}><dt>{f.replace("_g","")}</dt><dd>{items.length?displayNutrient(totals?.[f]):"—"} {f==="calories"?"kcal":"g"}</dd></div>)}</dl>
      <p className="small muted">Unknown nutrients remain unknown. Complete carbohydrate, protein, fat and fiber facts are required for forecasting.</p>
      <label>Meal time with timezone<input value={at} onChange={e=>{setAt(e.target.value);changed();}} placeholder="2026-01-01T12:00:00Z"/><span className="small muted">Use the source clock for virtual data. Include Z or an explicit offset. Profile timezone: {account?.preferences.timezone}.</span></label>
      <label>Meal slot<select value={mealType} onChange={e=>{setMealType(e.target.value);changed();}}><option value="">Unspecified</option>{["breakfast","lunch","dinner","snack"].map(s=><option key={s} value={s}>{s}</option>)}</select></label>
      <label>Status<select value={state} onChange={e=>{setState(e.target.value as "planned"|"logged");changed();}}><option value="planned">Planned — exclude from eaten totals</option><option value="logged">Eaten — include in nutrition</option></select></label>
      {state==="logged"&&<label>Eaten time with timezone<input value={consumedAt||at} onChange={e=>{setConsumedAt(e.target.value);changed();}}/></label>}
      <p className="small muted">Unsaved drafts stay in memory during app navigation. Reloading or closing the browser discards them. Signing out or changing source clears drafts.</p>
      <label className="confirmation"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/>I reviewed the food matches, grams, yield, time, status and sources.</label>
      <button className="button" disabled={!!busy||!confirmed||!valid||!name.trim()} onClick={()=>void action("Saving reviewed meal",async()=>{
        if(!requestKey.current)requestKey.current=crypto.randomUUID();
        drafts.write(draftKey,{mode,query,code,recipe,items,foods,ingredients,name,servings,portion,at,consumedAt,state,meal,requestKey:requestKey.current,mealType});
        const result=await api(mealId?`/meals/${mealId}`:"/meals",{method:mealId?"PATCH":"POST",body:JSON.stringify({name,recorded_at:at,state,meal_type:mealType||null,consumed_at:state==="logged"?(consumedAt||at):null,confirmed:true,idempotency_key:requestKey.current,items:items.map(i=>({food_id:i.food.id,grams:i.grams/servings*portion,expected_facts:expectedFacts(i.food)})),input_snapshot:{entry_method:mode,servings,portion,confirmed:true},...(mealId?{revision:meal?.revision}:{})})});drafts.clear(draftKey);router.push(`/meals/${result.meal_id}`);router.refresh();
      })}>{mealId?"Save new revision":"Save reviewed meal"}</button>
    </section></div></>;
}
