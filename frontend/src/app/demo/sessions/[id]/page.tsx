import { MealWorkflow } from "../../../../features/meal/MealWorkflow";
import { SimulationNutrition } from "../../../../features/simulation/SimulationNutrition";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <><MealWorkflow initialSourceId={id}/><SimulationNutrition sourceId={id}/></>;}
