"use client";
import { createContext, useContext, useState, type ReactNode } from "react";
import type { DraftItem, Food, Meal } from "../../lib/meal-facts";
export type MealDraft={mode:string;query:string;code:string;recipe:string;items:DraftItem[];foods:Food[];ingredients:{name:string;quantity:number;unit:string;needs_review:boolean}[];name:string;servings:number;portion:number;at:string;consumedAt:string;state:"planned"|"logged";meal?:Meal;requestKey:string;mealType:string};
type Store={read:(key:string)=>MealDraft|undefined;write:(key:string,draft:MealDraft)=>void;clear:(key:string)=>void};
const Context=createContext<Store|null>(null);
export function MealDrafts({children}:{children:ReactNode}) {
 const [store]=useState<Store>(()=>{const drafts=new Map<string,MealDraft>();return {read:key=>drafts.get(key),write:(key,draft)=>{drafts.set(key,draft);if(drafts.size>5){const first=drafts.keys().next().value;if(first&&first!==key)drafts.delete(first);}},clear:key=>drafts.delete(key)};});
 return <Context.Provider value={store}>{children}</Context.Provider>;
}
export function useMealDrafts(){const value=useContext(Context);if(!value)throw new Error("Draft scope unavailable");return value;}
